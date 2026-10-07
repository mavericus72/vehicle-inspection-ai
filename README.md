 # 🚗 Vehicle Inspection AI

 > An end-to-end computer vision system for automated vehicle inspection from video, combining vehicle detection, tracking, view classification, vehicle-part segmentation, damage detection, and automated PDF report generation.

---

 ## Overview

 **Vehicle Inspection AI** is an AI-powered vehicle inspection system designed to process vehicle inspection videos and generate a user-friendly inspection report.

 The system combines multiple computer vision components into a single inference pipeline rather than relying on one model for the entire inspection process.

 The pipeline identifies the primary vehicle, determines which vehicle views are available, extracts representative frames, identifies vehicle parts, detects visible damage, associates damage with vehicle parts, and evaluates the overall inspection.

 The final results are presented through a **human-readable PDF inspection report containing inspection information and visualized damage results**.

 The project has evolved from an initial YOLO-based detection prototype into a modular inference application exposed through an asynchronous FastAPI API.

---

 ## Key Features

- 🚘 Vehicle detection
- 🎯 Multi-object vehicle tracking
- 🚗 Primary vehicle selection
- 🔄 Front / Rear / Left / Right view classification
- 📊 Vehicle coverage estimation
- 🖼️ Representative-frame extraction
- 🔍 Vehicle-part segmentation
- 🧩 Vehicle-part semantic mapping
- ⚠️ Vehicle damage detection
- 🔗 Damage-to-part association
- 📋 Inspection evaluation
- 📄 Automated PDF inspection reports
- 🌐 Asynchronous FastAPI API
- 📝 Application logging
- ⚙️ Configurable model paths and inference parameters

---

 ## System Architecture

```
                    Vehicle Inspection Video
                              │
                              ▼
                     ┌─────────────────┐
                     │ Vehicle Tracker │
                     └────────┬────────┘
                              │
                              ├── vehicles
                              ├── frame cache
                              └── total frames
                              │
                              ▼
                  ┌────────────────────────┐
                  │ Primary Vehicle        │
                  │ Selector               │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │ Coverage Pipeline      │
                  │                        │
                  │ View Classification     │
                  │ Coverage Estimation     │
                  └───────────┬────────────┘
                              │
                              ▼
               ┌─────────────────────────────┐
               │ Representative Frame       │
               │ Extractor                   │
               └─────────────┬───────────────┘
                             │
                             ▼
             ┌─────────────────────────────────┐
             │ Vehicle Part Segmentation       │
             │              +                  │
             │ Part Mapping                    │
             └───────────────┬─────────────────┘
                             │
                             ▼
                   Vehicle Parts
                             │
                             ▼
                  ┌─────────────────┐
                  │ Damage Detection│
                  └────────┬────────┘
                           │
                           ▼
                Damage ↔ Part Association
                           │
                           ▼
                 Inspection Evaluation
                           │
                           ▼
                  PDF Report Generator
                           │
                           ▼
                User-Friendly PDF Report
```

---

 # Inspection Pipeline

 ## 1\. Vehicle Detection

 The pipeline initially uses a pre-trained **YOLO11n** model for lightweight vehicle detection. The model benefits from COCO pre-training, which provides common vehicle categories such as cars, trucks, buses, and motorcycles. YOLO11n was selected initially because video inspection requires processing a large number of frames and a lightweight model allows faster experimentation. **YOLO26n** is also included in the project configuration as an available vehicle detection model for further experimentation and deployment optimization.

 ## 2\. Vehicle Tracking

 Vehicle tracking is performed to maintain the identity of detected vehicles across video frames. Tracking prevents the system from treating every detection as a new vehicle and allows the inspection pipeline to follow the primary vehicle throughout the video. Tracking information is also used by downstream coverage and frame-selection components. ByteTrack was explored as the tracking approach during the early development stages.

 ## 3\. Primary Vehicle Selection

 When multiple vehicles appear in a video, the system selects the vehicle that should be treated as the inspection target. The selected primary vehicle becomes the input for subsequent inspection stages. This prevents unrelated vehicles in the background from influencing the inspection results. The primary vehicle information is maintained throughout the inspection session.

 ## 4\. Vehicle View Classification

 A custom vehicle-view classification model was developed to identify the vehicle's **front, rear, left, and right** views. A dedicated dataset of **2,000 images** was created with approximately 500 images for each view. The dataset was divided using a **70/15/15 train/validation/test split**. The view classifier provides confidence information that is subsequently used by the coverage-estimation stage.

 ## 5\. Coverage Estimation

 Coverage estimation determines which vehicle views are sufficiently represented in the inspection video. The system originally relied heavily on frame-by-frame information, which caused significant memory consumption during development. The pipeline was later modified to use limited frame information, cached observations, confidence-based decisions, and representative frames. A view is considered available only when the pipeline can obtain a valid representative image for that view.

 ## 6\. Representative Frame Extraction

 The representative-frame extractor selects the best actual vehicle image or crop for downstream processing. This is intentionally different from simply selecting the best classification observation. The selected frame is used by later vehicle-part and damage-processing stages. This approach also reduces unnecessary processing of every frame and helped address memory and execution-time problems.

 ## 7\. Vehicle-Part Segmentation

 A custom vehicle-part segmentation model was developed using polygon-based annotations created with CVAT. The initial dataset was expanded and simplified to focus on practical vehicle components, resulting in **18 vehicle-part classes**. The model produces segmentation information including class, confidence, bounding box, and mask information. The segmentation output is passed to the vehicle-part extraction and mapping stages.

 ## 8\. Vehicle-Part Mapping

 Raw segmentation classes are converted into semantic vehicle-part names using a dedicated `PartMapper`. The mapper also resolves the correct vehicle side where required, allowing outputs such as **left mirror** and **right mirror** instead of ambiguous generic part names. This mapping was integrated with the vehicle-part extractor and segmentation pipeline. The resulting semantic vehicle-part information is stored as part of the inspection result.

 ## 9\. Damage Detection

 Vehicle damage detection uses a custom **YOLO11n segmentation model** trained on annotated vehicle-damage data. The damage dataset contained approximately **3,091 selected images**, with **2,149 images receiving final annotations** for the training workflow. The initial damage categories included dent, scratch, crack, broken, paint peeling, pierced, and tear, although some categories had insufficient training data and were excluded from the current training evaluation. Damage detection remains an active development area, with crack detection showing stronger practical performance than several other damage categories.

 ## 10\. Damage ↔ Part Association

 Detected damage is associated with the corresponding vehicle part using the available vehicle-part and damage information. The association stage combines spatial and semantic information rather than treating damage as an isolated detection. This allows the inspection result to move toward statements such as a specific type of damage being associated with a specific vehicle component. The association is then passed to the inspection evaluation and reporting stages.

 ## 11\. Inspection Evaluation

 The inspection evaluation stage combines coverage, vehicle-part information, damage information, and other pipeline outputs into a unified inspection result. The system supports videos containing **one, two, three, or four vehicle views** rather than requiring all four views to be present. Several edge cases were identified and corrected during development, including missing representative frames and videos with incomplete vehicle coverage. This makes the pipeline more tolerant of real-world inspection videos.

 ## 12\. PDF Report Generation

 The final inspection information is converted into a user-friendly PDF report. The report includes inspection information, detected vehicle-part information, damage results, and visualized damage outputs where available. Damage visualization images are generated and incorporated into the final report rather than requiring the user to inspect raw model output. The goal is to make the output understandable to a non-technical vehicle-inspection user.

---

 # Models

 ## Vehicle Detection

 ### YOLO11n

 A pre-trained **YOLO11n** model was initially selected for vehicle detection because of its low computational cost and fast iteration speed. Its COCO pre-training provides common vehicle classes that are useful during the initial detection and tracking stages.

 ### YOLO26n

 **YOLO26n** is also included in the project's model configuration as an available lightweight vehicle detector. It provides an additional model option for experimentation and future accuracy/performance comparisons.

---

 ## Vehicle View Classification

 A custom YOLO-based classification model was trained to classify:

```
Front
Rear
Left
Right
```

 The dataset contained approximately **2,000 images**, divided into training, validation, and test sets using a 70/15/15 split.

---

 ## Vehicle-Part Segmentation

 A custom YOLO segmentation model was trained using polygon annotations created in CVAT.

 The final vehicle-part dataset contained:

- **2,149 annotated images**
- **18 vehicle-part classes**
- Ultralytics YOLO segmentation format

 The model was integrated with:

```
VehiclePartSegmenter
        ↓
VehiclePartExtractor
        ↓
PartMapper
        ↓
PartPipeline
```

---

 ## Vehicle Damage Detection

 A custom **YOLO11n segmentation model** was trained for vehicle damage detection.

 Current damage categories included:

```
dent
scratch
crack
broken
paint_peeling
pierced
tear
```

 Some categories currently have insufficient training data and require additional dataset development before reliable evaluation.

---

 # Dataset & Annotation

 Several custom datasets were created during development.

 ### Vehicle View Dataset

 Approximately **2,000 images** were collected and categorized into four vehicle views:

| View | Approx. Images |
| --- | --- |
| Front | 500 |
| Rear | 500 |
| Left | 500 |
| Right | 500 |
| **Total** | **2,000** |

The dataset was split into approximately **70% training, 15% validation, and 15% testing**.

 ### Vehicle-Part Dataset

 Vehicle-part images were annotated using **CVAT** with polygon segmentation annotations. The dataset evolved during development to reduce ambiguous or overly granular classes and eventually contained **18 practical vehicle-part classes**.

 ### Damage Dataset

 The selected damage dataset contained approximately **3,091 images** before annotation filtering. A final set of **2,149 annotated images** was used for the current training workflow.

 The annotated damage dataset contained approximately **12,570 damage instances**, with **12,514 annotated instances** reported during dataset analysis.

---

 # Training & Evaluation Metrics

 ## Damage Model

 The current YOLO11n segmentation damage model was trained at an image size of **640 × 640**.

 The best checkpoint was obtained around **epoch 70**, while training eventually stopped around epoch 90 because of a lack of further improvement.

 Validation results:

| Metric | Result |
| --- | --- |
| Validation images | 429 |
| Validation instances | 2,932 |
| Box Precision | 0.563 |
| Box Recall | 0.279 |
| Box mAP50 | **0.280** |
| Box mAP50-95 | **0.165** |
| Mask Precision | 0.568 |
| Mask Recall | 0.247 |
| Mask mAP50 | **0.250** |
| Mask mAP50-95 | **0.134** |

A separate confidence-threshold evaluation produced a best observed F1 score of approximately **0.0115 at a confidence threshold of 0.35**. These results indicate that the current damage model requires further dataset balancing, annotation refinement, and training before it can be considered production-grade.

 The strongest practical behavior observed during validation was for **crack detection**, while dent, scratch, broken, and other low-frequency classes require additional work.

---

 # Performance Optimization

 A major part of the project involved reducing memory consumption and inference time.

 The initial implementation attempted to retain large amounts of frame information, which caused the process to consume available RAM. The pipeline was redesigned to use controlled frame caching and representative-frame extraction rather than retaining every full-resolution frame.

 Performance testing showed an optimized pipeline execution time of approximately:

```
Total pipeline time: 266.79 seconds
≈ 4 minutes 27 seconds
```

 The tracking stage was the dominant computational component:

```
Tracking time: 254.02 seconds
```

 An earlier run required more than 18 minutes, with report generation alone taking approximately 530 seconds. After addressing unnecessary directory searches and report-generation overhead, a later report-generation run completed in approximately **6 seconds**.

 These optimizations significantly improved the practicality of running the complete inspection pipeline on a local machine.

---

 # API Architecture

 The inference pipeline is exposed through an asynchronous FastAPI application.

```
Client
  │
  │ POST video
  ▼
FastAPI
  │
  ▼
InspectionRunner
  │
  ▼
InspectionService
  │
  ▼
run_inspection()
  │
  ▼
InferencePipeline
  │
  ├── Detection
  ├── Tracking
  ├── Coverage
  ├── View Classification
  ├── Representative Frames
  ├── Part Segmentation
  ├── Damage Detection
  ├── Damage Association
  └── Report Generation
  │
  ▼
PDF Inspection Report
```

 The API immediately returns a job ID while the inspection continues asynchronously.

---

 # API Endpoints

 ### Health Check

```
GET /api/v1/health
```

 Returns the current API health status.

 ### Create Inspection

```
POST /api/v1/inspections
```

 Accepts a vehicle inspection video through multipart form upload and returns a job ID.

 Example response:

```
{
  "job_id": "example-job-id",
  "status": "queued"
}
```

 ### Get Inspection Status

```
GET /api/v1/inspections/{job_id}
```

 Returns the current state of the asynchronous inspection job.

 Possible states include:

```
queued
running
completed
failed
```

 ### Download PDF Report

```
GET /api/v1/inspections/{job_id}/report/pdf
```

 Returns the generated user-friendly PDF inspection report.

---

 # Example Workflow

```
1. Upload inspection video
           ↓
2. Receive job_id
           ↓
3. Poll inspection status
           ↓
4. Pipeline processes video
           ↓
5. Vehicle views are evaluated
           ↓
6. Representative frames are selected
           ↓
7. Vehicle parts are segmented
           ↓
8. Damage is detected
           ↓
9. Damage is associated with parts
           ↓
10. Inspection is evaluated
           ↓
11. PDF report is generated
           ↓
12. Report is available through the API
```

---

 # Project Structure

```
vehicle-inspection-ai/
│
├── app.py
├── api.py
├── requirements.txt
│
├── models/
│   ├── classification/
│   ├── detection/
│   ├── vehicle_damage_detection/
│   └── vehicle_part_segmenter/
│
├── data/
├── outputs/
├── reports/
├── logs/
│
└── src/
    ├── api/
    │   ├── __init__.py
    │   ├── routes.py
    │   └── schemas.py
    │
    ├── config/
    │   ├── __init__.py
    │   └── settings.py
    │
    ├── inspection/
    ├── pipeline/
    ├── tracking/
    ├── vision/
    │
    └── services/
        ├── inspection_job.py
        ├── inspection_job_service.py
        ├── inspection_result.py
        ├── inspection_runner.py
        ├── inspection_service.py
        └── logging_service.py
```

---

 # Technology Stack

| Technology | Purpose |
| --- | --- |
| Python | Core application |
| PyTorch | Deep-learning inference |
| Ultralytics | YOLO model training/inference |
| YOLO11n | Vehicle/damage model components |
| YOLO26n | Vehicle detection model option |
| OpenCV | Video and image processing |
| NumPy | Numerical processing |
| Matplotlib | Visualization |
| FastAPI | API layer |
| Uvicorn | ASGI server |
| Pydantic | API schemas |
| CVAT | Dataset annotation |
| ReportLab | PDF report generation |

---

 # Deployment

 The application has been tested locally as an asynchronous FastAPI service and successfully exposed through a public Cloudflare Tunnel for demonstration.

 The current architecture is intentionally lightweight and preserves the existing inference pipeline:

```
FastAPI
   ↓
BackgroundTasks
   ↓
InspectionRunner
   ↓
InspectionService
   ↓
Existing Inference Pipeline
```

 The application is currently designed primarily for a **single-process demonstration/development deployment**. Production-scale deployment would require additional consideration for persistent job storage, shared workers, persistent file storage, GPU/CPU resources, and long-running inference workloads.

---

 # Current Limitations

 The vehicle-part identification and semantic mapping pipeline is currently stronger than the damage-detection component.

 The current damage model has limited performance on several classes because of class imbalance, insufficient examples for some damage types, difficult visual distinctions, and the nature of the available datasets.

 Some source images are close-up vehicle-part images rather than complete vehicle inspection views, creating a domain gap between training data and real inspection videos.

 The system also currently relies on local filesystem storage for uploaded videos, intermediate outputs, logs, and generated reports.

 The asynchronous job store is currently in memory, which is suitable for the current demonstration architecture but is not sufficient for multi-instance production deployment.

---

 # Future Improvements

- Improve damage dataset quality and class balance.
- Increase the number of real-world vehicle inspection videos used for validation.
- Improve detection of low-frequency damage categories.
- Benchmark YOLO11n and YOLO26n under the same inspection workload.
- Improve GPU/CPU inference performance.
- Further optimize tracking and frame processing.
- Introduce persistent job storage.
- Introduce persistent/object storage for videos and reports.
- Improve production logging and monitoring.
- Deploy the inference workload on appropriate GPU-enabled infrastructure.
- Add authentication and API security.
- Develop a dedicated inspection frontend.

---

 # Project Status

 **Current status: Working prototype / public demonstration**

 The complete inspection workflow is operational from video upload through asynchronous processing, vehicle analysis, damage/part processing, and PDF report generation.

 The primary focus of the next development stage is improving **damage-detection reliability, performance, persistent storage, and production deployment architecture**.

---

 ## Deployment Note

 **Free deployment was limited by platform constraints: Docker — storage limitations; Render — insufficient RAM for the ML workload; Hugging Face — required paid service for the required deployment setup; Oracle Cloud VM — required payment/credit-card verification.**

 This version deliberately makes the project sound like an **AI engineering system**, rather than just a collection of YOLO models. It also keeps the weaker damage metrics transparent instead of hiding them, which I think is important if the repository will be reviewed by technical people.
