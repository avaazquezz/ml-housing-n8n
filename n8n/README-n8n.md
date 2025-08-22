# N8N - Housing Price Prediction Workflow

This n8n workflow integrates the housing price prediction API with a Telegram bot for a more accessible user experience.

## Files
- `n8n/housing-predict-workflow.json` - Main n8n workflow
- `n8n/My workflow.json` - Additional workflow configuration

## Import Workflow
1. Open n8n Editor (http://localhost:5678)
2. Go to **Workflows** → **Import**
3. Select the `housing-predict-workflow.json` file

## 🤖 Usage via Telegram Bot

### Production Bot
The workflow is connected to a Telegram bot for easy usage:

**🔗 Telegram Bot: [@HouseValuePredictorBot](https://t.me/HouseValuePredictorBot)**

### How to use the bot:
1. Open the link: https://t.me/HouseValuePredictorBot
2. Start conversation with `/start`
3. Send housing data in the requested format
4. Receive price prediction instantly

### Required parameters:
- **MedInc**: Median income (1-15)
- **HouseAge**: House age in years (1-50)
- **AveRooms**: Average rooms (3-15)
- **AveBedrms**: Average bedrooms (0.5-3)
- **Population**: Area population (1-10000)
- **AveOccup**: Average occupancy (1-10)
- **Latitude**: Latitude (32-42)
- **Longitude**: Longitude (-125 to -114)

## 🔧 Local Setup (For Development)

### Requirements
- Docker and Docker Compose
- Port 5678 available for n8n

### Run locally:
```bash
# Run full stack
docker-compose up

# Only n8n
docker-compose up n8n
```

### Local URLs:
- **n8n Editor**: http://localhost:5678
- **API**: http://localhost:8000
- **n8n Credentials**: admin / 1234

## 🚀 Workflow Components

### 1. Webhook Trigger
- Receives data from Telegram bot
- Endpoint: `/webhook/housing-predict`

### 2. Data Processing
- Validates and formats input data
- Converts parameters to API required format

### 3. ML API Call
- Calls prediction API (http://api:8000/predict)
- Sends formatted data

### 4. Response Formatting
- Processes API response
- Formats price for Telegram display

### 5. Telegram Response
- Sends result back to user
- Includes estimated price and additional information

## ⚙️ Telegram Bot Configuration

### Required environment variables:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBHOOK_URL=your_webhook_url_here
```

### Bot commands:
- `/start` - Start conversation
- `/help` - Show help
- `/predict` - Start price prediction

## 🧪 Testing (Development Only)

### Test local webhook:
```bash
curl -X POST "http://localhost:5678/webhook-test/housing-predict" \
  -H "Content-Type: application/json" \
  -d '{
    "MedInc": 8.0,
    "HouseAge": 15,
    "AveRooms": 5.0,
    "AveBedrms": 1.0,
    "Population": 1000,
    "AveOccup": 2.0,
    "Latitude": 34.0,
    "Longitude": -118.0
  }'
```

### Test API directly:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "MedInc": 8.0,
    "HouseAge": 15,
    "AveRooms": 5.0,
    "AveBedrms": 1.0,
    "Population": 1000,
    "AveOccup": 2.0,
    "Latitude": 34.0,
    "Longitude": -118.0
  }'
```

## 📊 Usage Example

**User in Telegram:**
```
🏠 Housing Price Predictor

Enter housing data:
Median income: 8
House age: 15
Average rooms: 5
Average bedrooms: 1
Population: 1000
Average occupancy: 2
Latitude: 34
Longitude: -118
```

**Bot response:**
```
🏡 Estimated price: $421,296

📍 Location: Lat 34.0, Long -118.0
🏠 Features: 5 rooms, 1 bedroom, 15 years old
👥 Area: 1000 people, 2 occupants/house
💰 Area median income: $80,000
```

## 🔄 Production

### To activate in production:
1. Configure Telegram webhook
2. Activate workflow in n8n
3. Verify API accessibility
4. Test bot with real data

### Monitoring:
- n8n logs for debugging
- API metrics
- Telegram bot status
