package com.org.pragatidhara.network.services

import com.org.pragatidhara.data.model.*
import retrofit2.Response
import retrofit2.http.*

/**
 * Vehicle Management API Service
 * Handles all vehicle-related operations
 */
interface VehicleApiService {
    
    @POST("vehicles/register")
    suspend fun registerVehicle(
        @Body request: VehicleRegistrationRequest
    ): Response<VehicleRegistrationResponse>
    
    @GET("vehicles/{vehicleId}")
    suspend fun getVehicleProfile(
        @Path("vehicleId") vehicleId: String
    ): Response<VehicleProfile>
    
    @PUT("vehicles/{vehicleId}")
    suspend fun updateVehicleProfile(
        @Path("vehicleId") vehicleId: String,
        @Body updateRequest: VehicleUpdateRequest
    ): Response<VehicleProfile>
    
    @DELETE("vehicles/{vehicleId}")
    suspend fun deregisterVehicle(
        @Path("vehicleId") vehicleId: String
    ): Response<DeregistrationResponse>
    
    // Maintenance endpoints
    @GET("vehicles/{vehicleId}/maintenance")
    suspend fun getMaintenanceHistory(
        @Path("vehicleId") vehicleId: String,
        @Query("page") page: Int = 0,
        @Query("size") size: Int = 20
    ): Response<MaintenanceHistoryResponse>
    
    @POST("vehicles/{vehicleId}/maintenance")
    suspend fun addMaintenanceRecord(
        @Path("vehicleId") vehicleId: String,
        @Body maintenanceRecord: MaintenanceRecord
    ): Response<MaintenanceUpdateResponse>
    
    @GET("vehicles/{vehicleId}/maintenance/predictions")
    suspend fun getMaintenancePredictions(
        @Path("vehicleId") vehicleId: String
    ): Response<MaintenancePredictionResponse>
    
    // Emissions endpoints
    @GET("vehicles/{vehicleId}/emissions/profile")
    suspend fun getEmissionProfile(
        @Path("vehicleId") vehicleId: String
    ): Response<EmissionProfile>
    
    @POST("vehicles/{vehicleId}/emissions/test")
    suspend fun submitEmissionTest(
        @Path("vehicleId") vehicleId: String,
        @Body emissionTestResult: EmissionTestResult
    ): Response<EmissionTestSubmissionResponse>
    
    @GET("vehicles/{vehicleId}/emissions/compliance")
    suspend fun checkComplianceStatus(
        @Path("vehicleId") vehicleId: String
    ): Response<ComplianceStatus>
    
    // Analytics endpoints
    @GET("vehicles/{vehicleId}/analytics/usage")
    suspend fun getUsageAnalytics(
        @Path("vehicleId") vehicleId: String,
        @Query("period") period: String = "month"
    ): Response<UsageAnalytics>
    
    @GET("vehicles/{vehicleId}/analytics/efficiency")
    suspend fun getEfficiencyTrends(
        @Path("vehicleId") vehicleId: String,
        @Query("period") period: String = "month"
    ): Response<EfficiencyTrends>
    
    @GET("vehicles/{vehicleId}/analytics/carbon-footprint")
    suspend fun getCarbonFootprintAnalysis(
        @Path("vehicleId") vehicleId: String,
        @Query("period") period: String = "month"
    ): Response<CarbonFootprintAnalysis>
}

/**
 * AI Routing & Prediction API Service
 * Handles traffic prediction and route optimization
 */
interface AIRoutingApiService {
    
    @POST("ai-routing/predict-traffic")
    suspend fun predictTraffic(
        @Body request: TrafficPredictionRequest
    ): Response<TrafficPredictionResponse>
    
    @POST("ai-routing/optimize-route")
    suspend fun optimizeRoute(
        @Body request: RouteOptimizationRequest
    ): Response<RouteOptimizationResponse>
    
    @POST("ai-routing/conversational-assistant")
    suspend fun processConversationalQuery(
        @Body request: ConversationalRequest
    ): Response<ConversationalResponse>
    
    @GET("ai-routing/traffic-hotspots")
    suspend fun getTrafficHotspots(
        @Query("lat") latitude: Double,
        @Query("lng") longitude: Double,
        @Query("radius") radius: Double = 10.0
    ): Response<List<TrafficHotspot>>
    
    @POST("ai-routing/report-traffic")
    suspend fun reportTrafficIncident(
        @Body incident: TrafficIncidentReport
    ): Response<IncidentReportResponse>
    
    @GET("ai-routing/alternative-routes")
    suspend fun getAlternativeRoutes(
        @Query("origin_lat") originLat: Double,
        @Query("origin_lng") originLng: Double,
        @Query("dest_lat") destLat: Double,
        @Query("dest_lng") destLng: Double,
        @Query("vehicle_type") vehicleType: String
    ): Response<AlternativeRoutesResponse>
    
    @POST("ai-routing/route-feedback")
    suspend fun submitRouteFeedback(
        @Body feedback: RouteFeedback
    ): Response<FeedbackSubmissionResponse>
}

/**
 * Real-time Data Processing API Service
 * Handles telemetry and real-time updates
 */
interface RealTimeApiService {
    
    @POST("realtime/vehicle-telemetry")
    suspend fun sendVehicleTelemetry(
        @Body telemetryBatch: VehicleTelemetryBatch
    ): Response<TelemetryProcessingResponse>
    
    @GET("realtime/traffic-updates")
    suspend fun getTrafficUpdates(
        @Query("lat") latitude: Double,
        @Query("lng") longitude: Double,
        @Query("radius") radius: Double = 5.0
    ): Response<List<TrafficUpdate>>
    
    @POST("realtime/location-update")
    suspend fun sendLocationUpdate(
        @Body locationUpdate: LocationUpdate
    ): Response<LocationUpdateResponse>
    
    @GET("realtime/nearby-vehicles")
    suspend fun getNearbyVehicles(
        @Query("lat") latitude: Double,
        @Query("lng") longitude: Double,
        @Query("radius") radius: Double = 1.0
    ): Response<List<NearbyVehicle>>
    
    @POST("realtime/emergency-alert")
    suspend fun sendEmergencyAlert(
        @Body emergencyAlert: EmergencyAlert
    ): Response<EmergencyAlertResponse>
    
    @GET("realtime/road-conditions")
    suspend fun getRoadConditions(
        @Query("route_id") routeId: String
    ): Response<RoadConditionsResponse>
}

/**
 * Green Rewards Management API Service
 * Handles sustainability rewards and gamification
 */
interface RewardsApiService {
    
    @POST("rewards/calculate-trip-rewards")
    suspend fun calculateTripRewards(
        @Body request: TripRewardsRequest
    ): Response<TripRewardsResponse>
    
    @GET("rewards/user/{userId}/balance")
    suspend fun getRewardsBalance(
        @Path("userId") userId: String
    ): Response<RewardsBalance>
    
    @GET("rewards/user/{userId}/history")
    suspend fun getRewardsHistory(
        @Path("userId") userId: String,
        @Query("page") page: Int = 0,
        @Query("size") size: Int = 20
    ): Response<RewardsHistoryResponse>
    
    @POST("rewards/redeem")
    suspend fun redeemRewards(
        @Body request: RewardsRedemptionRequest
    ): Response<RedemptionResponse>
    
    @GET("rewards/redemption-options")
    suspend fun getRedemptionOptions(): Response<List<RedemptionOption>>
    
    @GET("rewards/leaderboard")
    suspend fun getLeaderboard(
        @Query("period") period: String = "month",
        @Query("type") type: String = "carbon_saved"
    ): Response<LeaderboardResponse>
    
    @POST("rewards/challenges/accept")
    suspend fun acceptChallenge(
        @Body request: ChallengeAcceptanceRequest
    ): Response<ChallengeAcceptanceResponse>
    
    @GET("rewards/challenges/available")
    suspend fun getAvailableChallenges(
        @Query("user_id") userId: String
    ): Response<List<Challenge>>
    
    @POST("rewards/achievements/claim")
    suspend fun claimAchievement(
        @Body request: AchievementClaimRequest
    ): Response<AchievementClaimResponse>
    
    @GET("rewards/user/{userId}/sustainability-score")
    suspend fun getSustainabilityScore(
        @Path("userId") userId: String,
        @Query("period") period: String = "month"
    ): Response<SustainabilityScore>
}