package com.org.pragatidhara.network

import com.google.gson.Gson
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import okhttp3.*
import android.util.Log
import com.org.pragatidhara.data.model.RealTimeUpdate
import com.org.pragatidhara.data.model.WebSocketMessage
import com.org.pragatidhara.utils.TokenManager
import javax.inject.Inject
import javax.inject.Singleton

/**
 * WebSocket manager for real-time updates
 * Handles traffic updates, vehicle telemetry, and notifications
 */
@Singleton
class WebSocketManager @Inject constructor(
    private val okHttpClient: OkHttpClient,
    private val tokenManager: TokenManager
) {
    
    companion object {
        private const val TAG = "WebSocketManager"
        private const val WS_BASE_URL = "wss://api.pragatidhara.com/ws"
        private const val RECONNECT_DELAY = 3000L
        private const val MAX_RECONNECT_ATTEMPTS = 5
    }
    
    private var webSocket: WebSocket? = null
    private val gson = Gson()
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private var reconnectAttempts = 0
    private var isConnected = false
    
    // Real-time data flows
    private val _realTimeUpdates = MutableSharedFlow<RealTimeUpdate>(replay = 1)
    val realTimeUpdates: SharedFlow<RealTimeUpdate> = _realTimeUpdates.asSharedFlow()
    
    private val _trafficUpdates = MutableSharedFlow<TrafficUpdate>(replay = 1)
    val trafficUpdates: SharedFlow<TrafficUpdate> = _trafficUpdates.asSharedFlow()
    
    private val _vehicleTelemetry = MutableSharedFlow<VehicleTelemetryUpdate>(replay = 1)
    val vehicleTelemetry: SharedFlow<VehicleTelemetryUpdate> = _vehicleTelemetry.asSharedFlow()
    
    private val _connectionStatus = MutableSharedFlow<ConnectionStatus>(replay = 1)
    val connectionStatus: SharedFlow<ConnectionStatus> = _connectionStatus.asSharedFlow()
    
    private val webSocketListener = object : WebSocketListener() {
        
        override fun onOpen(webSocket: WebSocket, response: Response) {
            Log.d(TAG, "WebSocket connection opened")
            isConnected = true
            reconnectAttempts = 0
            
            scope.launch {
                _connectionStatus.emit(ConnectionStatus.Connected)
            }
            
            // Subscribe to relevant topics
            subscribeToTopics()
        }
        
        override fun onMessage(webSocket: WebSocket, text: String) {
            Log.d(TAG, "WebSocket message received: $text")
            
            try {
                val message = gson.fromJson(text, WebSocketMessage::class.java)
                handleIncomingMessage(message)
            } catch (e: Exception) {
                Log.e(TAG, "Error parsing WebSocket message: $text", e)
            }
        }
        
        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            Log.e(TAG, "WebSocket connection failed", t)
            isConnected = false
            
            scope.launch {
                _connectionStatus.emit(ConnectionStatus.Failed(t.message ?: "Unknown error"))
                
                // Attempt reconnection
                if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    scheduleReconnection()
                } else {
                    _connectionStatus.emit(ConnectionStatus.Disconnected)
                }
            }
        }
        
        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
            Log.d(TAG, "WebSocket connection closed: $reason")
            isConnected = false
            
            scope.launch {
                _connectionStatus.emit(ConnectionStatus.Disconnected)
            }
        }
    }
    
    /**
     * Connect to WebSocket server
     */
    fun connect() {
        if (isConnected) {
            Log.d(TAG, "WebSocket already connected")
            return
        }
        
        val token = tokenManager.getAccessToken()
        val request = Request.Builder()
            .url(WS_BASE_URL)
            .addHeader("Authorization", "Bearer $token")
            .build()
            
        webSocket = okHttpClient.newWebSocket(request, webSocketListener)
        
        scope.launch {
            _connectionStatus.emit(ConnectionStatus.Connecting)
        }
    }
    
    /**
     * Disconnect from WebSocket server
     */
    fun disconnect() {
        webSocket?.close(1000, "Normal closure")
        webSocket = null
        isConnected = false
        
        scope.launch {
            _connectionStatus.emit(ConnectionStatus.Disconnected)
        }
    }
    
    /**
     * Subscribe to real-time topics
     */
    private fun subscribeToTopics() {
        val userId = tokenManager.getCurrentUserId()
        
        // Subscribe to traffic updates for user's location
        subscribeToTrafficUpdates(userId)
        
        // Subscribe to vehicle telemetry updates
        subscribeToVehicleTelemetry(userId)
        
        // Subscribe to general notifications
        subscribeToNotifications(userId)
    }
    
    /**
     * Subscribe to traffic updates
     */
    private fun subscribeToTrafficUpdates(userId: String) {
        val subscriptionMessage = WebSocketMessage(
            type = "SUBSCRIBE",
            topic = "traffic-updates",
            payload = mapOf(
                "userId" to userId,
                "radius" to 10.0 // 10km radius
            )
        )
        sendMessage(subscriptionMessage)
    }
    
    /**
     * Subscribe to vehicle telemetry updates
     */
    private fun subscribeToVehicleTelemetry(userId: String) {
        val subscriptionMessage = WebSocketMessage(
            type = "SUBSCRIBE",
            topic = "vehicle-telemetry",
            payload = mapOf("userId" to userId)
        )
        sendMessage(subscriptionMessage)
    }
    
    /**
     * Subscribe to notifications
     */
    private fun subscribeToNotifications(userId: String) {
        val subscriptionMessage = WebSocketMessage(
            type = "SUBSCRIBE",
            topic = "notifications",
            payload = mapOf("userId" to userId)
        )
        sendMessage(subscriptionMessage)
    }
    
    /**
     * Send location update
     */
    fun sendLocationUpdate(latitude: Double, longitude: Double) {
        val locationMessage = WebSocketMessage(
            type = "LOCATION_UPDATE",
            topic = "location",
            payload = mapOf(
                "latitude" to latitude,
                "longitude" to longitude,
                "timestamp" to System.currentTimeMillis()
            )
        )
        sendMessage(locationMessage)
    }
    
    /**
     * Send traffic report
     */
    fun sendTrafficReport(report: TrafficIncidentReport) {
        val reportMessage = WebSocketMessage(
            type = "TRAFFIC_REPORT",
            topic = "traffic-incidents",
            payload = mapOf(
                "report" to report,
                "timestamp" to System.currentTimeMillis()
            )
        )
        sendMessage(reportMessage)
    }
    
    /**
     * Handle incoming WebSocket messages
     */
    private fun handleIncomingMessage(message: WebSocketMessage) {
        scope.launch {
            when (message.topic) {
                "traffic-updates" -> {
                    val trafficUpdate = gson.fromJson(
                        gson.toJson(message.payload),
                        TrafficUpdate::class.java
                    )
                    _trafficUpdates.emit(trafficUpdate)
                }
                
                "vehicle-telemetry" -> {
                    val telemetryUpdate = gson.fromJson(
                        gson.toJson(message.payload),
                        VehicleTelemetryUpdate::class.java
                    )
                    _vehicleTelemetry.emit(telemetryUpdate)
                }
                
                "notifications" -> {
                    val realTimeUpdate = gson.fromJson(
                        gson.toJson(message.payload),
                        RealTimeUpdate::class.java
                    )
                    _realTimeUpdates.emit(realTimeUpdate)
                }
                
                else -> {
                    Log.d(TAG, "Unknown message topic: ${message.topic}")
                }
            }
        }
    }
    
    /**
     * Send message to WebSocket server
     */
    private fun sendMessage(message: WebSocketMessage) {
        if (!isConnected) {
            Log.w(TAG, "WebSocket not connected, cannot send message")
            return
        }
        
        try {
            val json = gson.toJson(message)
            webSocket?.send(json)
        } catch (e: Exception) {
            Log.e(TAG, "Error sending WebSocket message", e)
        }
    }
    
    /**
     * Schedule reconnection after delay
     */
    private fun scheduleReconnection() {
        scope.launch {
            kotlinx.coroutines.delay(RECONNECT_DELAY)
            reconnectAttempts++
            Log.d(TAG, "Attempting reconnection ($reconnectAttempts/$MAX_RECONNECT_ATTEMPTS)")
            connect()
        }
    }
}

/**
 * WebSocket connection status
 */
sealed class ConnectionStatus {
    object Connecting : ConnectionStatus()
    object Connected : ConnectionStatus()
    object Disconnected : ConnectionStatus()
    data class Failed(val error: String) : ConnectionStatus()
}

/**
 * Traffic update data class
 */
data class TrafficUpdate(
    val id: String,
    val location: Location,
    val severity: String,
    val description: String,
    val timestamp: Long,
    val affectedRoutes: List<String>
)

/**
 * Vehicle telemetry update data class
 */
data class VehicleTelemetryUpdate(
    val vehicleId: String,
    val speed: Double,
    val fuelLevel: Double,
    val emissions: EmissionReading,
    val location: Location,
    val timestamp: Long
)

/**
 * Location data class
 */
data class Location(
    val latitude: Double,
    val longitude: Double
)

/**
 * Emission reading data class
 */
data class EmissionReading(
    val co2: Double,
    val nox: Double,
    val pm25: Double
)