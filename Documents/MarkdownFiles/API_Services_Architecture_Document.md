# PragatiDhara API Services Layer Architecture

## 🏗️ **API Services Architecture Overview**

### **Deployment Strategy: Cloud-Based Backend + Edge Computing**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRAGATIDHARA API ECOSYSTEM                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐ │
│  │   Mobile App    │    │   Web Dashboard  │    │  Admin Panel│ │
│  │   (Android)     │    │   (React/Vue)    │    │  (React)    │ │
│  └─────────┬───────┘    └─────────┬────────┘    └──────┬──────┘ │
│            │                      │                    │        │
├────────────┼──────────────────────┼────────────────────┼────────┤
│            │                      │                    │        │
│  ┌─────────▼──────────────────────▼────────────────────▼──────┐ │
│  │              API GATEWAY (Spring Cloud Gateway)           │ │
│  │          Load Balancing + Authentication + Rate Limiting  │ │
│  └─────────────────────────┬───────────────────────────────────┘ │
│                            │                                     │
├────────────────────────────┼─────────────────────────────────────┤
│         MICROSERVICES LAYER │                                     │
│  ┌─────────────┐  ┌─────────▼─────┐  ┌──────────────┐  ┌────────┐ │
│  │   Vehicle   │  │  AI Route     │  │  Real-time   │  │ Green  │ │
│  │ Management  │  │  Prediction   │  │    Data      │  │Rewards │ │
│  │   Service   │  │   Service     │  │ Processing   │  │Service │ │
│  │(Spring Boot)│  │(Spring Boot + │  │   Service    │  │(Spring │ │
│  │             │  │   AI/ML)      │  │(Spring Boot +│  │ Boot)  │ │
│  │             │  │               │  │  WebSockets) │  │        │ │
│  └─────────────┘  └───────────────┘  └──────────────┘  └────────┘ │
│                                                                   │
├───────────────────────────────────────────────────────────────────┤
│              SHARED INFRASTRUCTURE LAYER                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │   MongoDB   │  │ Redis Cache │  │  PostgreSQL │  │   Kafka  │ │
│  │  (Vehicle   │  │ (Sessions + │  │ (Analytics  │  │(Real-time│ │
│  │    Data)    │  │   Cache)    │  │    Data)    │  │Messages) │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🌐 **Where API Services Will Run**

### **Recommended Architecture: Cloud-Based Spring Boot Microservices**

#### **Option 1: AWS Cloud Infrastructure (Recommended)**
```yaml
deployment_environment:
  platform: "AWS EKS (Kubernetes)"
  compute: "EC2 instances (t3.medium/large)"
  load_balancer: "Application Load Balancer"
  auto_scaling: "Horizontal Pod Autoscaler"
  
infrastructure_components:
  api_gateway: "AWS API Gateway + Spring Cloud Gateway"
  container_registry: "Amazon ECR"
  monitoring: "CloudWatch + Prometheus"
  logging: "ELK Stack (Elasticsearch, Logstash, Kibana)"
  
databases:
  primary_db: "Amazon RDS (PostgreSQL)"
  document_db: "Amazon DocumentDB (MongoDB compatible)"
  cache: "Amazon ElastiCache (Redis)"
  time_series: "Amazon Timestream (for IoT data)"

estimated_costs:
  development: "$200-400/month"
  production: "$800-1500/month"
  scaling_potential: "Up to 100K+ concurrent users"
```

#### **Option 2: Google Cloud Platform**
```yaml
deployment_environment:
  platform: "Google Kubernetes Engine (GKE)"
  compute: "Compute Engine (n1-standard-2/4)"
  
infrastructure_components:
  api_gateway: "Google Cloud Endpoints"
  ai_services: "Google AI Platform (for ML models)"
  storage: "Google Cloud Storage"
  
databases:
  primary_db: "Cloud SQL (PostgreSQL)"
  document_db: "Firestore"
  cache: "Memorystore (Redis)"
```

#### **Why NOT on Mobile Phone:**
❌ **Limited Resources**: Mobile devices have CPU/memory constraints  
❌ **Battery Drain**: Continuous API serving would drain battery rapidly  
❌ **Network Reliability**: Mobile networks are inconsistent for serving APIs  
❌ **Security**: Exposing APIs from mobile devices creates security vulnerabilities  
❌ **Scalability**: Cannot handle multiple concurrent users  

---

## 🔧 **API Services Architecture Details**

### **1. Vehicle Management Service**

#### **A. Service Overview**
```java
@RestController
@RequestMapping("/api/v1/vehicles")
@CrossOrigin(origins = "*")
public class VehicleManagementController {
    
    @Autowired
    private VehicleService vehicleService;
    
    @Autowired
    private EmissionService emissionService;
    
    // Core vehicle operations
    @PostMapping("/register")
    public ResponseEntity<VehicleRegistrationResponse> registerVehicle(
        @RequestBody @Valid VehicleRegistrationRequest request
    ) {
        try {
            Vehicle vehicle = vehicleService.registerNewVehicle(request);
            EmissionProfile emissionProfile = emissionService.calculateEmissionProfile(vehicle);
            
            return ResponseEntity.ok(VehicleRegistrationResponse.builder()
                .vehicleId(vehicle.getId())
                .registrationNumber(vehicle.getRegistrationNumber())
                .emissionProfile(emissionProfile)
                .greenCreditsEligible(vehicle.isEcoFriendly())
                .build());
                
        } catch (VehicleAlreadyExistsException e) {
            return ResponseEntity.badRequest()
                .body(VehicleRegistrationResponse.error("Vehicle already registered"));
        }
    }
    
    @GetMapping("/{vehicleId}/profile")
    public ResponseEntity<VehicleProfile> getVehicleProfile(@PathVariable String vehicleId) {
        Vehicle vehicle = vehicleService.findById(vehicleId);
        VehicleProfile profile = VehicleProfile.builder()
            .basicInfo(vehicle.getBasicInfo())
            .emissionData(vehicle.getEmissionData())
            .maintenanceHistory(vehicle.getMaintenanceHistory())
            .sustainabilityScore(calculateSustainabilityScore(vehicle))
            .build();
            
        return ResponseEntity.ok(profile);
    }
    
    @PutMapping("/{vehicleId}/maintenance")
    public ResponseEntity<MaintenanceUpdateResponse> updateMaintenance(
        @PathVariable String vehicleId,
        @RequestBody MaintenanceRecord maintenanceRecord
    ) {
        vehicleService.addMaintenanceRecord(vehicleId, maintenanceRecord);
        
        // Trigger AI-based maintenance predictions
        MaintenancePrediction prediction = vehicleService.predictNextMaintenance(vehicleId);
        
        return ResponseEntity.ok(MaintenanceUpdateResponse.builder()
            .updated(true)
            .nextMaintenancePredictor(prediction)
            .greenCreditsEarned(calculateMaintenanceGreenCredits(maintenanceRecord))
            .build());
    }
}
```

#### **B. API Endpoints Structure**
```yaml
vehicle_management_api:
  base_url: "/api/v1/vehicles"
  
  endpoints:
    registration:
      - "POST /register" # Register new vehicle
      - "GET /{vehicleId}" # Get vehicle details
      - "PUT /{vehicleId}" # Update vehicle info
      - "DELETE /{vehicleId}" # Deregister vehicle
    
    maintenance:
      - "GET /{vehicleId}/maintenance" # Maintenance history
      - "POST /{vehicleId}/maintenance" # Add maintenance record
      - "GET /{vehicleId}/maintenance/predictions" # AI maintenance predictions
    
    emissions:
      - "GET /{vehicleId}/emissions/profile" # Emission profile
      - "POST /{vehicleId}/emissions/test" # Add emission test results
      - "GET /{vehicleId}/emissions/compliance" # Check compliance status
      
    analytics:
      - "GET /{vehicleId}/analytics/usage" # Usage patterns
      - "GET /{vehicleId}/analytics/efficiency" # Fuel efficiency trends
      - "GET /{vehicleId}/analytics/carbon-footprint" # Carbon footprint analysis
```

### **2. AI Route Prediction & Decision Engine Service**

#### **A. Service Architecture**
```java
@RestController
@RequestMapping("/api/v1/ai-routing")
public class AIRoutePredictionController {
    
    @Autowired
    private TrafficPredictionService trafficPredictionService;
    
    @Autowired
    private RouteOptimizationService routeOptimizationService;
    
    @Autowired
    private GeminiIntegrationService geminiService;
    
    @PostMapping("/predict-traffic")
    public ResponseEntity<TrafficPredictionResponse> predictTraffic(
        @RequestBody TrafficPredictionRequest request
    ) {
        
        // Use hybrid AI approach (local models + Gemini when needed)
        CompletableFuture<LocalTrafficPrediction> localPrediction = 
            trafficPredictionService.predictUsingLocalModels(request);
            
        CompletableFuture<GeminiTrafficInsight> geminiInsight = 
            geminiService.getTrafficInsights(request);
        
        // Combine predictions for enhanced accuracy
        TrafficPrediction combinedPrediction = CompletableFuture.allOf(
            localPrediction, geminiInsight
        ).thenApply(v -> {
            return fusePredictions(localPrediction.join(), geminiInsight.join());
        }).join();
        
        return ResponseEntity.ok(TrafficPredictionResponse.builder()
            .prediction(combinedPrediction)
            .confidence(combinedPrediction.getConfidence())
            .timeHorizon(request.getTimeHorizon())
            .alternativeRoutes(generateAlternativeRoutes(request))
            .build());
    }
    
    @PostMapping("/optimize-route")
    public ResponseEntity<RouteOptimizationResponse> optimizeRoute(
        @RequestBody RouteOptimizationRequest request
    ) {
        
        // Multi-objective optimization
        OptimizationObjectives objectives = OptimizationObjectives.builder()
            .travelTime(0.30f)
            .fuelConsumption(0.25f)
            .carbonEmissions(0.25f)
            .trafficAvoidance(0.20f)
            .build();
        
        RouteOptimizationResult result = routeOptimizationService.optimizeRoute(
            request.getOrigin(),
            request.getDestination(),
            request.getVehicleProfile(),
            request.getUserPreferences(),
            objectives
        );
        
        return ResponseEntity.ok(RouteOptimizationResponse.builder()
            .optimizedRoute(result.getOptimalRoute())
            .alternativeRoutes(result.getAlternativeRoutes())
            .sustainabilityScore(result.getSustainabilityScore())
            .estimatedSavings(result.getEstimatedSavings())
            .aiRecommendations(result.getAIRecommendations())
            .build());
    }
    
    @PostMapping("/conversational-assistant")
    public ResponseEntity<ConversationalResponse> processConversationalQuery(
        @RequestBody ConversationalRequest request
    ) {
        
        // Use Gemini for complex conversational queries
        GeminiResponse geminiResponse = geminiService.processNaturalLanguageQuery(
            request.getUserQuery(),
            request.getContext()
        );
        
        // Extract actionable insights from Gemini response
        ActionableInsights insights = extractActionableInsights(geminiResponse);
        
        return ResponseEntity.ok(ConversationalResponse.builder()
            .naturalLanguageResponse(geminiResponse.getText())
            .structuredRecommendations(insights.getRecommendations())
            .actionableSteps(insights.getActionableSteps())
            .confidence(geminiResponse.getConfidence())
            .build());
    }
}
```

#### **B. ML Model Integration Architecture**
```java
@Service
public class HybridAIRoutingService {
    
    // Local CPU-optimized models
    @Autowired
    private LSTMTrafficPredictor lstmPredictor; // 3.2MB model
    
    @Autowired
    private XGBoostRouteOptimizer xgboostOptimizer; // 1.8MB model
    
    @Autowired
    private RandomForestEmissionCalculator emissionCalculator; // 2.1MB model
    
    // Cloud-based AI services
    @Autowired
    private GeminiProService geminiProService;
    
    @Autowired
    private GeminiFlashService geminiFlashService;
    
    public RoutingDecision makeRoutingDecision(RoutingContext context) {
        
        // 1. Quick local predictions for basic scenarios
        LocalRoutingResult localResult = processWithLocalModels(context);
        
        // 2. Enhanced reasoning for complex scenarios using Gemini
        if (context.getComplexity() > COMPLEXITY_THRESHOLD) {
            GeminiEnhancedResult geminiResult = processWithGemini(context, localResult);
            return combineResults(localResult, geminiResult);
        }
        
        return localResult.toRoutingDecision();
    }
    
    private LocalRoutingResult processWithLocalModels(RoutingContext context) {
        
        // Traffic prediction using LSTM
        TrafficPrediction trafficPrediction = lstmPredictor.predict(
            context.getHistoricalTrafficData(),
            context.getCurrentConditions()
        );
        
        // Route optimization using XGBoost
        RouteOptimization routeOptimization = xgboostOptimizer.optimize(
            context.getOrigin(),
            context.getDestination(),
            trafficPrediction
        );
        
        // Emission calculation using Random Forest
        EmissionEstimate emissionEstimate = emissionCalculator.calculate(
            routeOptimization.getOptimalRoute(),
            context.getVehicleProfile()
        );
        
        return LocalRoutingResult.builder()
            .trafficPrediction(trafficPrediction)
            .routeOptimization(routeOptimization)
            .emissionEstimate(emissionEstimate)
            .confidence(calculateCombinedConfidence())
            .build();
    }
}
```

### **3. Real-time Data Processing Service**

#### **A. Streaming Architecture**
```java
@RestController
@RequestMapping("/api/v1/realtime")
public class RealTimeDataController {
    
    @Autowired
    private KafkaProducerService kafkaProducer;
    
    @Autowired
    private WebSocketSessionManager webSocketManager;
    
    @Autowired
    private RealTimeAnalyticsService analyticsService;
    
    @PostMapping("/vehicle-telemetry")
    public ResponseEntity<TelemetryProcessingResponse> processVehicleTelemetry(
        @RequestBody VehicleTelemetryBatch telemetryBatch
    ) {
        
        // Validate and preprocess telemetry data
        ProcessedTelemetryBatch processedBatch = preprocessTelemetryData(telemetryBatch);
        
        // Stream to Kafka for real-time processing
        kafkaProducer.sendTelemetryData("vehicle-telemetry-topic", processedBatch);
        
        // Immediate analytics for real-time response
        RealTimeInsights insights = analyticsService.generateImmediateInsights(processedBatch);
        
        // Push to connected WebSocket clients
        webSocketManager.broadcastToVehicleSubscribers(
            telemetryBatch.getVehicleId(),
            insights
        );
        
        return ResponseEntity.ok(TelemetryProcessingResponse.builder()
            .processed(true)
            .immediateInsights(insights)
            .streamingTopicId("vehicle-telemetry-topic")
            .build());
    }
    
    @MessageMapping("/traffic-updates")
    @SendTo("/topic/traffic-updates")
    public TrafficUpdateBroadcast handleTrafficUpdate(TrafficUpdateMessage message) {
        
        // Process traffic update through AI prediction pipeline
        TrafficImpactAnalysis impact = analyticsService.analyzeTrafficImpact(message);
        
        // Generate affected route recommendations
        List<AffectedRoute> affectedRoutes = analyticsService.findAffectedRoutes(
            message.getLocation(),
            message.getSeverity()
        );
        
        return TrafficUpdateBroadcast.builder()
            .originalMessage(message)
            .impactAnalysis(impact)
            .affectedRoutes(affectedRoutes)
            .alternativeRecommendations(generateAlternativeRecommendations(affectedRoutes))
            .timestamp(Instant.now())
            .build();
    }
}
```

#### **B. Real-time Processing Pipeline**
```java
@Component
public class RealTimeStreamProcessor {
    
    @KafkaListener(topics = "vehicle-telemetry-topic")
    public void processVehicleTelemetry(VehicleTelemetryBatch telemetryBatch) {
        
        // 1. Real-time anomaly detection
        AnomalyDetectionResult anomalies = detectAnomalies(telemetryBatch);
        
        // 2. Emission calculation in real-time
        RealTimeEmissionData emissions = calculateRealTimeEmissions(telemetryBatch);
        
        // 3. Behavioral pattern analysis
        BehaviorPattern behavior = analyzeDrivingBehavior(telemetryBatch);
        
        // 4. Store processed data
        storeProcessedTelemetry(telemetryBatch, anomalies, emissions, behavior);
        
        // 5. Trigger alerts if necessary
        if (anomalies.hasSignificantAnomalies()) {
            triggerAlerts(telemetryBatch.getVehicleId(), anomalies);
        }
        
        // 6. Update real-time dashboards
        updateRealTimeDashboards(telemetryBatch.getVehicleId(), emissions, behavior);
    }
    
    @KafkaListener(topics = "traffic-updates-topic")
    public void processTrafficUpdates(TrafficUpdateMessage trafficUpdate) {
        
        // 1. Update traffic prediction models with real-time data
        trafficPredictionService.updateWithRealTimeData(trafficUpdate);
        
        // 2. Recalculate affected routes
        List<String> affectedRouteIds = findAffectedRoutes(trafficUpdate);
        
        // 3. Send real-time notifications to affected users
        for (String routeId : affectedRouteIds) {
            List<String> affectedUsers = findUsersOnRoute(routeId);
            sendRealTimeNotifications(affectedUsers, trafficUpdate);
        }
        
        // 4. Update route optimization algorithms
        routeOptimizationService.updateTrafficConditions(trafficUpdate);
    }
}
```

### **4. Green Rewards Management Service**

#### **A. Rewards Engine**
```java
@RestController
@RequestMapping("/api/v1/rewards")
public class GreenRewardsController {
    
    @Autowired
    private RewardsCalculationService rewardsService;
    
    @Autowired
    private SustainabilityMetricsService sustainabilityService;
    
    @Autowired
    private BlockchainRewardsService blockchainService; // For transparent rewards
    
    @PostMapping("/calculate-trip-rewards")
    public ResponseEntity<TripRewardsResponse> calculateTripRewards(
        @RequestBody TripRewardsRequest request
    ) {
        
        // Calculate environmental impact of the trip
        EnvironmentalImpact impact = sustainabilityService.calculateTripImpact(
            request.getRoute(),
            request.getVehicleProfile(),
            request.getDrivingBehavior()
        );
        
        // Calculate rewards based on sustainability metrics
        RewardsCalculation rewards = rewardsService.calculateRewards(
            impact,
            request.getUserProfile(),
            request.getTripContext()
        );
        
        // Record rewards in blockchain for transparency
        String rewardsTransactionId = blockchainService.recordRewards(
            request.getUserId(),
            rewards
        );
        
        return ResponseEntity.ok(TripRewardsResponse.builder()
            .greenCreditsEarned(rewards.getGreenCredits())
            .carbonSaved(impact.getCarbonSaved())
            .sustainabilityScore(rewards.getSustainabilityScore())
            .rewardsBreakdown(rewards.getBreakdown())
            .blockchainTransactionId(rewardsTransactionId)
            .nextLevelRequirement(calculateNextLevelRequirement(request.getUserId()))
            .build());
    }
    
    @GetMapping("/user/{userId}/rewards-history")
    public ResponseEntity<RewardsHistoryResponse> getRewardsHistory(
        @PathVariable String userId,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        
        Page<RewardsTransaction> rewardsHistory = rewardsService.getRewardsHistory(
            userId, PageRequest.of(page, size)
        );
        
        // Calculate aggregated statistics
        RewardsStatistics statistics = rewardsService.calculateRewardsStatistics(userId);
        
        return ResponseEntity.ok(RewardsHistoryResponse.builder()
            .rewardsHistory(rewardsHistory.getContent())
            .totalPages(rewardsHistory.getTotalPages())
            .totalGreenCredits(statistics.getTotalGreenCredits())
            .totalCarbonSaved(statistics.getTotalCarbonSaved())
            .currentLevel(statistics.getCurrentLevel())
            .leaderboardRank(statistics.getLeaderboardRank())
            .build());
    }
    
    @PostMapping("/redeem-rewards")
    public ResponseEntity<RedemptionResponse> redeemRewards(
        @RequestBody RewardsRedemptionRequest request
    ) {
        
        // Validate redemption eligibility
        RedemptionEligibility eligibility = rewardsService.checkRedemptionEligibility(
            request.getUserId(),
            request.getRedemptionType(),
            request.getAmount()
        );
        
        if (!eligibility.isEligible()) {
            return ResponseEntity.badRequest()
                .body(RedemptionResponse.error(eligibility.getErrorMessage()));
        }
        
        // Process redemption
        RedemptionResult result = rewardsService.processRedemption(request);
        
        // Record redemption in blockchain
        String redemptionTransactionId = blockchainService.recordRedemption(
            request.getUserId(),
            result
        );
        
        return ResponseEntity.ok(RedemptionResponse.builder()
            .redeemed(true)
            .redemptionId(result.getRedemptionId())
            .blockchainTransactionId(redemptionTransactionId)
            .remainingCredits(result.getRemainingCredits())
            .redemptionDetails(result.getDetails())
            .build());
    }
}
```

---

## 📱 **Mobile App API Integration**

### **1. API Client Architecture (Android)**

#### **A. Retrofit API Client Setup**
```kotlin
// File: android-app/app/src/main/java/com/org/pragatidhara/network/ApiClient.kt

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    
    private const val BASE_URL = "https://api.pragatidhara.com/api/v1/"
    
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(AuthenticationInterceptor())
            .addInterceptor(LoggingInterceptor())
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .addCallAdapterFactory(CoroutineCallAdapterFactory())
            .build()
    }
    
    @Provides
    @Singleton
    fun provideVehicleApiService(retrofit: Retrofit): VehicleApiService {
        return retrofit.create(VehicleApiService::class.java)
    }
    
    @Provides
    @Singleton
    fun provideAIRoutingApiService(retrofit: Retrofit): AIRoutingApiService {
        return retrofit.create(AIRoutingApiService::class.java)
    }
    
    @Provides
    @Singleton
    fun provideRealTimeApiService(retrofit: Retrofit): RealTimeApiService {
        return retrofit.create(RealTimeApiService::class.java)
    }
    
    @Provides
    @Singleton
    fun provideRewardsApiService(retrofit: Retrofit): RewardsApiService {
        return retrofit.create(RewardsApiService::class.java)
    }
}
```

#### **B. API Service Interfaces**
```kotlin
// File: android-app/app/src/main/java/com/org/pragatidhara/network/VehicleApiService.kt

interface VehicleApiService {
    
    @POST("vehicles/register")
    suspend fun registerVehicle(
        @Body request: VehicleRegistrationRequest
    ): Response<VehicleRegistrationResponse>
    
    @GET("vehicles/{vehicleId}")
    suspend fun getVehicleProfile(
        @Path("vehicleId") vehicleId: String
    ): Response<VehicleProfile>
    
    @PUT("vehicles/{vehicleId}/maintenance")
    suspend fun updateMaintenance(
        @Path("vehicleId") vehicleId: String,
        @Body maintenanceRecord: MaintenanceRecord
    ): Response<MaintenanceUpdateResponse>
    
    @GET("vehicles/{vehicleId}/emissions/profile")
    suspend fun getEmissionProfile(
        @Path("vehicleId") vehicleId: String
    ): Response<EmissionProfile>
}

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
}

interface RealTimeApiService {
    
    @POST("realtime/vehicle-telemetry")
    suspend fun sendVehicleTelemetry(
        @Body telemetryBatch: VehicleTelemetryBatch
    ): Response<TelemetryProcessingResponse>
    
    @GET("realtime/traffic-updates")
    suspend fun getTrafficUpdates(
        @Query("location") location: String,
        @Query("radius") radius: Double
    ): Response<List<TrafficUpdate>>
}

interface RewardsApiService {
    
    @POST("rewards/calculate-trip-rewards")
    suspend fun calculateTripRewards(
        @Body request: TripRewardsRequest
    ): Response<TripRewardsResponse>
    
    @GET("rewards/user/{userId}/rewards-history")
    suspend fun getRewardsHistory(
        @Path("userId") userId: String,
        @Query("page") page: Int = 0,
        @Query("size") size: Int = 20
    ): Response<RewardsHistoryResponse>
    
    @POST("rewards/redeem-rewards")
    suspend fun redeemRewards(
        @Body request: RewardsRedemptionRequest
    ): Response<RedemptionResponse>
}
```

### **2. Repository Pattern Implementation**

#### **A. API Repository with Error Handling**
```kotlin
// File: android-app/app/src/main/java/com/org/pragatidhara/data/repository/VehicleRepository.kt

@Singleton
class VehicleRepository @Inject constructor(
    private val vehicleApiService: VehicleApiService,
    private val localDatabase: VehicleDao,
    private val networkMonitor: NetworkMonitor
) {
    
    suspend fun registerVehicle(
        vehicleData: VehicleRegistrationRequest
    ): Result<VehicleRegistrationResponse> {
        
        return try {
            if (!networkMonitor.isOnline()) {
                // Queue for later sync when online
                localDatabase.insertPendingRegistration(vehicleData)
                return Result.failure(NetworkException("Offline - queued for sync"))
            }
            
            val response = vehicleApiService.registerVehicle(vehicleData)
            
            if (response.isSuccessful) {
                response.body()?.let { registrationResponse ->
                    // Cache successful registration locally
                    localDatabase.insertVehicle(registrationResponse.toVehicleEntity())
                    Result.success(registrationResponse)
                } ?: Result.failure(EmptyResponseException())
            } else {
                handleApiError(response)
            }
            
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getVehicleProfile(vehicleId: String): Result<VehicleProfile> {
        
        return try {
            // Try to get from local cache first
            val cachedVehicle = localDatabase.getVehicleById(vehicleId)
            
            if (networkMonitor.isOnline()) {
                // Fetch latest from API
                val response = vehicleApiService.getVehicleProfile(vehicleId)
                
                if (response.isSuccessful) {
                    response.body()?.let { profile ->
                        // Update local cache
                        localDatabase.updateVehicle(profile.toVehicleEntity())
                        Result.success(profile)
                    } ?: Result.failure(EmptyResponseException())
                } else {
                    // Fall back to cached data if API fails
                    cachedVehicle?.let { 
                        Result.success(it.toVehicleProfile()) 
                    } ?: handleApiError(response)
                }
            } else {
                // Offline - return cached data
                cachedVehicle?.let {
                    Result.success(it.toVehicleProfile())
                } ?: Result.failure(NetworkException("No cached data available"))
            }
            
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private fun handleApiError(response: Response<*>): Result.Failure {
        return when (response.code()) {
            401 -> Result.failure(AuthenticationException("Authentication required"))
            403 -> Result.failure(AuthorizationException("Access denied"))
            404 -> Result.failure(NotFoundException("Resource not found"))
            429 -> Result.failure(RateLimitException("Rate limit exceeded"))
            500 -> Result.failure(ServerException("Server error"))
            else -> Result.failure(ApiException("API error: ${response.code()}"))
        }
    }
}
```

### **3. Real-time WebSocket Integration**

#### **A. WebSocket Manager for Real-time Updates**
```kotlin
// File: android-app/app/src/main/java/com/org/pragatidhara/network/WebSocketManager.kt

@Singleton
class WebSocketManager @Inject constructor(
    private val okHttpClient: OkHttpClient
) {
    
    private var webSocket: WebSocket? = null
    private val _realTimeUpdates = MutableSharedFlow<RealTimeUpdate>()
    val realTimeUpdates: SharedFlow<RealTimeUpdate> = _realTimeUpdates.asSharedFlow()
    
    private val webSocketListener = object : WebSocketListener() {
        
        override fun onOpen(webSocket: WebSocket, response: okhttp3.Response) {
            Log.d("WebSocket", "Connection opened")
            // Subscribe to relevant topics
            subscribeToTrafficUpdates()
            subscribeToVehicleTelemetry()
        }
        
        override fun onMessage(webSocket: WebSocket, text: String) {
            try {
                val update = gson.fromJson(text, RealTimeUpdate::class.java)
                _realTimeUpdates.tryEmit(update)
            } catch (e: Exception) {
                Log.e("WebSocket", "Error parsing message: $text", e)
            }
        }
        
        override fun onFailure(webSocket: WebSocket, t: Throwable, response: okhttp3.Response?) {
            Log.e("WebSocket", "Connection failed", t)
            // Implement reconnection logic
            scheduleReconnection()
        }
        
        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
            Log.d("WebSocket", "Connection closed: $reason")
        }
    }
    
    fun connect() {
        val request = Request.Builder()
            .url("wss://api.pragatidhara.com/ws")
            .build()
            
        webSocket = okHttpClient.newWebSocket(request, webSocketListener)
    }
    
    fun disconnect() {
        webSocket?.close(1000, "Normal closure")
        webSocket = null
    }
    
    private fun subscribeToTrafficUpdates() {
        val subscriptionMessage = WebSocketMessage(
            type = "SUBSCRIBE",
            topic = "traffic-updates",
            payload = mapOf("userId" to getCurrentUserId())
        )
        sendMessage(subscriptionMessage)
    }
    
    private fun sendMessage(message: WebSocketMessage) {
        val json = gson.toJson(message)
        webSocket?.send(json)
    }
}
```

---

## 🔒 **Security & Authentication**

### **1. JWT-based Authentication**
```kotlin
// Authentication interceptor for API calls
class AuthenticationInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val originalRequest = chain.request()
        
        val token = tokenManager.getAccessToken()
        
        val authenticatedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .header("X-API-Version", "v1")
            .build()
            
        return chain.proceed(authenticatedRequest)
    }
}
```

### **2. API Rate Limiting & Caching**
```kotlin
// Network cache interceptor
class CacheInterceptor : Interceptor {
    
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val request = chain.request()
        val response = chain.proceed(request)
        
        // Cache GET requests for 5 minutes
        return if (request.method == "GET") {
            response.newBuilder()
                .header("Cache-Control", "public, max-age=300")
                .build()
        } else {
            response
        }
    }
}
```

---

## 🚀 **Deployment Architecture**

### **Spring Boot Microservices Deployment Configuration**

#### **Docker Configuration**
```dockerfile
# Dockerfile for each microservice
FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/pragatidhara-*.jar app.jar

EXPOSE 8080

ENV SPRING_PROFILES_ACTIVE=production

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

#### **Kubernetes Deployment**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vehicle-management-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vehicle-management-service
  template:
    metadata:
      labels:
        app: vehicle-management-service
    spec:
      containers:
      - name: vehicle-management-service
        image: pragatidhara/vehicle-management:latest
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: vehicle-management-service
spec:
  selector:
    app: vehicle-management-service
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

This comprehensive API services architecture provides:

✅ **Scalable microservices** running on cloud infrastructure  
✅ **Hybrid AI integration** (local models + cloud AI)  
✅ **Real-time data processing** with WebSockets and Kafka  
✅ **Comprehensive mobile app integration** with offline support  
✅ **Security** with JWT authentication and rate limiting  
✅ **Production-ready deployment** with Docker and Kubernetes  

The services will run on **cloud infrastructure (AWS/GCP)**, not on mobile devices, ensuring scalability, reliability, and optimal performance for the PragatiDhara ecosystem.