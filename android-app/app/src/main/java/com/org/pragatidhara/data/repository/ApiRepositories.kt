package com.org.pragatidhara.data.repository

import com.org.pragatidhara.data.local.VehicleDao
import com.org.pragatidhara.data.model.*
import com.org.pragatidhara.network.services.VehicleApiService
import com.org.pragatidhara.utils.NetworkMonitor
import com.org.pragatidhara.utils.Result
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for vehicle management operations
 * Implements offline-first approach with API synchronization
 */
@Singleton
class VehicleRepository @Inject constructor(
    private val vehicleApiService: VehicleApiService,
    private val vehicleDao: VehicleDao,
    private val networkMonitor: NetworkMonitor
) {
    
    /**
     * Register a new vehicle
     */
    suspend fun registerVehicle(
        vehicleData: VehicleRegistrationRequest
    ): Result<VehicleRegistrationResponse> {
        
        return try {
            if (!networkMonitor.isOnline()) {
                // Queue for later sync when online
                vehicleDao.insertPendingRegistration(vehicleData.toPendingRegistration())
                return Result.Success(
                    VehicleRegistrationResponse.offline(
                        message = "Vehicle registration queued - will sync when online"
                    )
                )
            }
            
            val response = vehicleApiService.registerVehicle(vehicleData)
            
            if (response.isSuccessful) {
                response.body()?.let { registrationResponse ->
                    // Cache successful registration locally
                    vehicleDao.insertVehicle(registrationResponse.toVehicleEntity())
                    Result.Success(registrationResponse)
                } ?: Result.Error(Exception("Empty response from server"))
            } else {
                handleApiError(response.code(), response.message())
            }
            
        } catch (e: Exception) {
            // Store locally and sync later
            vehicleDao.insertPendingRegistration(vehicleData.toPendingRegistration())
            Result.Error(e)
        }
    }
    
    /**
     * Get vehicle profile with offline support
     */
    suspend fun getVehicleProfile(vehicleId: String): Result<VehicleProfile> {
        
        return try {
            // Try to get from local cache first
            val cachedVehicle = vehicleDao.getVehicleById(vehicleId)
            
            if (networkMonitor.isOnline()) {
                // Fetch latest from API
                val response = vehicleApiService.getVehicleProfile(vehicleId)
                
                if (response.isSuccessful) {
                    response.body()?.let { profile ->
                        // Update local cache
                        vehicleDao.updateVehicle(profile.toVehicleEntity())
                        Result.Success(profile)
                    } ?: Result.Error(Exception("Empty response from server"))
                } else {
                    // Fall back to cached data if API fails
                    cachedVehicle?.let { 
                        Result.Success(it.toVehicleProfile()) 
                    } ?: handleApiError(response.code(), response.message())
                }
            } else {
                // Offline - return cached data
                cachedVehicle?.let {
                    Result.Success(it.toVehicleProfile())
                } ?: Result.Error(Exception("No cached data available offline"))
            }
            
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    /**
     * Get all user vehicles with offline support
     */
    fun getAllUserVehicles(userId: String): Flow<Result<List<VehicleProfile>>> = flow {
        
        try {
            // First emit cached data
            val cachedVehicles = vehicleDao.getUserVehicles(userId)
            if (cachedVehicles.isNotEmpty()) {
                emit(Result.Success(cachedVehicles.map { it.toVehicleProfile() }))
            }
            
            // Then try to fetch from API if online
            if (networkMonitor.isOnline()) {
                try {
                    // Note: This endpoint would need to be added to the API
                    // val response = vehicleApiService.getUserVehicles(userId)
                    // Handle response and update cache
                } catch (e: Exception) {
                    // Keep the cached data, don't emit error for network issues
                }
            }
            
        } catch (e: Exception) {
            emit(Result.Error(e))
        }
    }
    
    /**
     * Add maintenance record
     */
    suspend fun addMaintenanceRecord(
        vehicleId: String,
        maintenanceRecord: MaintenanceRecord
    ): Result<MaintenanceUpdateResponse> {
        
        return try {
            if (!networkMonitor.isOnline()) {
                // Store locally for later sync
                vehicleDao.insertPendingMaintenanceRecord(
                    maintenanceRecord.toPendingMaintenanceRecord(vehicleId)
                )
                return Result.Success(
                    MaintenanceUpdateResponse.offline(
                        message = "Maintenance record saved - will sync when online"
                    )
                )
            }
            
            val response = vehicleApiService.addMaintenanceRecord(vehicleId, maintenanceRecord)
            
            if (response.isSuccessful) {
                response.body()?.let { updateResponse ->
                    // Cache the maintenance record locally
                    vehicleDao.insertMaintenanceRecord(
                        maintenanceRecord.toMaintenanceEntity(vehicleId)
                    )
                    Result.Success(updateResponse)
                } ?: Result.Error(Exception("Empty response from server"))
            } else {
                handleApiError(response.code(), response.message())
            }
            
        } catch (e: Exception) {
            // Store locally for later sync
            vehicleDao.insertPendingMaintenanceRecord(
                maintenanceRecord.toPendingMaintenanceRecord(vehicleId)
            )
            Result.Error(e)
        }
    }
    
    /**
     * Get maintenance predictions using AI
     */
    suspend fun getMaintenancePredictions(vehicleId: String): Result<MaintenancePredictionResponse> {
        
        return try {
            if (!networkMonitor.isOnline()) {
                return Result.Error(Exception("Internet connection required for AI predictions"))
            }
            
            val response = vehicleApiService.getMaintenancePredictions(vehicleId)
            
            if (response.isSuccessful) {
                response.body()?.let { predictions ->
                    Result.Success(predictions)
                } ?: Result.Error(Exception("Empty response from server"))
            } else {
                handleApiError(response.code(), response.message())
            }
            
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    /**
     * Sync pending data when connection is restored
     */
    suspend fun syncPendingData(): Result<SyncResult> {
        
        return try {
            if (!networkMonitor.isOnline()) {
                return Result.Error(Exception("No internet connection for sync"))
            }
            
            val syncResult = SyncResult()
            
            // Sync pending vehicle registrations
            val pendingRegistrations = vehicleDao.getPendingRegistrations()
            for (pendingRegistration in pendingRegistrations) {
                try {
                    val response = vehicleApiService.registerVehicle(
                        pendingRegistration.toVehicleRegistrationRequest()
                    )
                    if (response.isSuccessful) {
                        vehicleDao.deletePendingRegistration(pendingRegistration.id)
                        syncResult.successfulRegistrations++
                    } else {
                        syncResult.failedRegistrations++
                    }
                } catch (e: Exception) {
                    syncResult.failedRegistrations++
                }
            }
            
            // Sync pending maintenance records
            val pendingMaintenance = vehicleDao.getPendingMaintenanceRecords()
            for (pendingRecord in pendingMaintenance) {
                try {
                    val response = vehicleApiService.addMaintenanceRecord(
                        pendingRecord.vehicleId,
                        pendingRecord.toMaintenanceRecord()
                    )
                    if (response.isSuccessful) {
                        vehicleDao.deletePendingMaintenanceRecord(pendingRecord.id)
                        syncResult.successfulMaintenanceRecords++
                    } else {
                        syncResult.failedMaintenanceRecords++
                    }
                } catch (e: Exception) {
                    syncResult.failedMaintenanceRecords++
                }
            }
            
            Result.Success(syncResult)
            
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    private fun handleApiError(code: Int, message: String): Result.Error {
        return when (code) {
            401 -> Result.Error(Exception("Authentication required"))
            403 -> Result.Error(Exception("Access denied"))
            404 -> Result.Error(Exception("Vehicle not found"))
            429 -> Result.Error(Exception("Rate limit exceeded. Please try again later"))
            500 -> Result.Error(Exception("Server error. Please try again later"))
            else -> Result.Error(Exception("API error ($code): $message"))
        }
    }
}

/**
 * Repository for AI routing and traffic prediction
 */
@Singleton
class AIRoutingRepository @Inject constructor(
    private val aiRoutingApiService: AIRoutingApiService,
    private val networkMonitor: NetworkMonitor
) {
    
    /**
     * Get traffic predictions using hybrid AI approach
     */
    suspend fun predictTraffic(
        request: TrafficPredictionRequest
    ): Result<TrafficPredictionResponse> {
        
        return try {
            if (!networkMonitor.isOnline()) {
                return Result.Error(Exception("Internet connection required for traffic predictions"))
            }
            
            val response = aiRoutingApiService.predictTraffic(request)
            
            if (response.isSuccessful) {
                response.body()?.let { prediction ->
                    Result.Success(prediction)
                } ?: Result.Error(Exception("Empty response from server"))
            } else {
                handleApiError(response.code(), response.message())
            }
            
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    /**
     * Optimize route using AI algorithms
     */
    suspend fun optimizeRoute(
        request: RouteOptimizationRequest
    ): Result<RouteOptimizationResponse> {
        
        return try {
            if (!networkMonitor.isOnline()) {
                return Result.Error(Exception("Internet connection required for route optimization"))
            }
            
            val response = aiRoutingApiService.optimizeRoute(request)
            
            if (response.isSuccessful) {
                response.body()?.let { optimization ->
                    Result.Success(optimization)
                } ?: Result.Error(Exception("Empty response from server"))
            } else {
                handleApiError(response.code(), response.message())
            }
            
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    /**
     * Process conversational queries using Gemini AI
     */
    suspend fun processConversationalQuery(
        request: ConversationalRequest
    ): Result<ConversationalResponse> {
        
        return try {
            if (!networkMonitor.isOnline()) {
                return Result.Error(Exception("Internet connection required for AI assistant"))
            }
            
            val response = aiRoutingApiService.processConversationalQuery(request)
            
            if (response.isSuccessful) {
                response.body()?.let { aiResponse ->
                    Result.Success(aiResponse)
                } ?: Result.Error(Exception("Empty response from server"))
            } else {
                handleApiError(response.code(), response.message())
            }
            
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    private fun handleApiError(code: Int, message: String): Result.Error {
        return when (code) {
            401 -> Result.Error(Exception("Authentication required"))
            403 -> Result.Error(Exception("Access denied"))
            404 -> Result.Error(Exception("Route not found"))
            429 -> Result.Error(Exception("Rate limit exceeded. Please try again later"))
            500 -> Result.Error(Exception("Server error. Please try again later"))
            else -> Result.Error(Exception("API error ($code): $message"))
        }
    }
}

/**
 * Repository for green rewards management
 */
@Singleton
class RewardsRepository @Inject constructor(
    private val rewardsApiService: RewardsApiService,
    private val networkMonitor: NetworkMonitor
) {
    
    /**
     * Calculate trip rewards
     */
    suspend fun calculateTripRewards(
        request: TripRewardsRequest
    ): Result<TripRewardsResponse> {
        
        return try {
            if (!networkMonitor.isOnline()) {
                return Result.Error(Exception("Internet connection required for rewards calculation"))
            }
            
            val response = rewardsApiService.calculateTripRewards(request)
            
            if (response.isSuccessful) {
                response.body()?.let { rewards ->
                    Result.Success(rewards)
                } ?: Result.Error(Exception("Empty response from server"))
            } else {
                handleApiError(response.code(), response.message())
            }
            
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    /**
     * Get user rewards balance
     */
    suspend fun getRewardsBalance(userId: String): Result<RewardsBalance> {
        
        return try {
            if (!networkMonitor.isOnline()) {
                return Result.Error(Exception("Internet connection required for rewards balance"))
            }
            
            val response = rewardsApiService.getRewardsBalance(userId)
            
            if (response.isSuccessful) {
                response.body()?.let { balance ->
                    Result.Success(balance)
                } ?: Result.Error(Exception("Empty response from server"))
            } else {
                handleApiError(response.code(), response.message())
            }
            
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    private fun handleApiError(code: Int, message: String): Result.Error {
        return when (code) {
            401 -> Result.Error(Exception("Authentication required"))
            403 -> Result.Error(Exception("Access denied"))
            404 -> Result.Error(Exception("User not found"))
            429 -> Result.Error(Exception("Rate limit exceeded. Please try again later"))
            500 -> Result.Error(Exception("Server error. Please try again later"))
            else -> Result.Error(Exception("API error ($code): $message"))
        }
    }
}

/**
 * Data class for sync results
 */
data class SyncResult(
    var successfulRegistrations: Int = 0,
    var failedRegistrations: Int = 0,
    var successfulMaintenanceRecords: Int = 0,
    var failedMaintenanceRecords: Int = 0
) {
    val totalSuccessful: Int
        get() = successfulRegistrations + successfulMaintenanceRecords
        
    val totalFailed: Int
        get() = failedRegistrations + failedMaintenanceRecords
        
    val isFullySuccessful: Boolean
        get() = totalFailed == 0 && totalSuccessful > 0
}