# n8n - housing-predict workflow

Files:
- n8n/housing-predict-workflow.json

## How to import
1. n8n Editor -> Workflows -> Import -> choose the json file.

## How to test locally
1. Start n8n (docker-compose or local).
2. Open workflow, click Webhook -> Listen for test event.
3. Run:
   curl -X POST "http://localhost:5678/webhook-test/housing-predict" \
     -H "Content-Type: application/json" \
     -d '{"MedInc":8,"HouseAge":15,"AveRooms":5,"AveBedrms":1,"Population":1000,"AveOccup":2,"Latitude":34,"Longitude":-118}'

## Production
- Activate workflow and use Production URL (from Webhook node).
