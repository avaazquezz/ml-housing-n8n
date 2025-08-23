# n8n Workflow Documentation

## Workflow Structure

The n8n workflow consists of the following nodes:

### 1. Telegram Trigger
- **Function**: Receives incoming messages from Telegram
- **Configuration**: Listens for message updates
- **Output**: Message data including chat_id and text content

### 2. Code Node
- **Function**: Parses and validates user input
- **Logic**: 
  - Detects `/start` command for welcome message
  - Validates comma-separated input (8 numerical values)
  - Routes to appropriate response path
- **Output**: Processed message with mode (welcome/predict/error)

### 3. Switch Node
- **Function**: Routes messages based on detected mode
- **Paths**:
  - **Welcome**: Shows usage instructions
  - **Predict**: Sends to API for prediction
  - **Error**: Shows error message for invalid input

### 4. HTTP Request Node
- **Function**: Calls the ML prediction API
- **Method**: POST
- **Endpoint**: `/predict-from-string`
- **Body**: User's comma-separated input values

### 5. Response Nodes
- **Send Prediction**: Returns formatted prediction result
- **Send Welcome**: Returns welcome and usage instructions  
- **Send Error**: Returns error message with valid format example

## Workflow Image

The workflow visual diagram shows the complete flow from Telegram input to API call and response formatting.

![Workflow Diagram Description]
- Telegram Trigger (purple) → Code Node (orange) → Switch Node (blue)
- Switch routes to three paths:
  - Top: HTTP Request (purple) → Send Prediction (blue)
  - Middle: Send Welcome (blue)
  - Bottom: Send Error (blue)

## Configuration Notes

- Ensure Telegram Bot credentials are properly configured
- Update API endpoint URL to match your deployment
- Test each path (welcome, predict, error) before production use
- Monitor webhook connectivity for reliability
