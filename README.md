SolarSentry
AI-Powered Solar Panel Inspection & Maintenance Assistant

SolarSentry is an AI-powered application designed to help users inspect solar panels, interpret operational measurements, identify potential issues, and generate actionable maintenance recommendations using image analysis and conversational AI.

The goal is to make solar panel monitoring more accessible by bringing visual inspection, electrical measurements, and AI-generated reports together in one interface.

 Key Features:

AI-Powered Inspection: Upload a solar panel image and generate an AI-assisted inspection report.
Electrical Performance Monitoring: Enter voltage, current, rated power, and irradiance measurements to support performance assessment.
Power Calculation:Calculate electrical output power using voltage and current measurements.
Maintenance Recommendations:Generate AI-assisted suggestions based on the inspection and available measurements.
Voice Interaction:Support voice input for a more accessible inspection workflow.
Report Generation:Produce readable inspection reports that can be downloaded for reference.
AI Follow-Up Chat:Ask additional questions about inspection findings and recommendations.
Text-to-Speech: Optionally narrate generated reports using ElevenLabs.
Web-Based Interface:Access the application through a browser using Streamlit.

How It Works:

1. Provide inspection data:Upload an image of a solar panel and enter available electrical and environmental measurements.
2. Analyze:The application sends the relevant information to a supported Gemini model for AI-assisted interpretation.
3. Generate a report:Receive a structured report with observations, potential concerns, and suggested maintenance actions.
4. Ask follow-up questions:Explore the report through the conversational interface.
5. Save and review:Download the generated report for future reference.

Technology Stack

Technology : Purpose 

| Python | Core application logic |
| Streamlit | Interactive web interface |
| Google Gemini API | AI-assisted image and text analysis |
| Google Gen AI SDK | Communication with Gemini |
| ElevenLabs API | Optional text-to-speech narration |
| Speech-to-text component | Voice input |
| python-dotenv | Local environment variable management |
| Requests | HTTP/API communication |

For Running Locally

Prerequisites:

- Python installed on your computer
- A Google Gemini API key
- An ElevenLabs API key if using narration
- Git (optional, for cloning the repository)

1. Clone the repository

```bash
git clone https://github.com/Pragya1602/solarsentry.git
cd solarsentry
```

2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure API keys

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

Replace the placeholders with your own API keys. Keep this file private and never commit it to GitHub.

5. Start the application

```bash
python -m streamlit run app.py
```

The terminal will display a local URL, usually `http://localhost:8501`. Open it in your browser.

Deployment

SolarSentry can be deployed using Streamlit Community Cloud.

1. Push the project files to GitHub.
2. Connect the repository to Streamlit Community Cloud.
3. Select `app.py` as the main application file.
4. Add the required API keys under the application's Settings → Secrets.

Configure secrets in TOML format:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
```

Ensure all required Python dependencies are listed in `requirements.txt`.

Security

- API keys should be stored in environment variables or Streamlit Secrets.
- The `.env` file and virtual environment should be excluded from Git using `.gitignore`.
- Never publish API keys, passwords, or other credentials in source code.

Limitations

- AI-generated observations are not a substitute for professional solar-system inspection.
- Image analysis depends on image quality, lighting, and the information available.
- Electrical measurements should be accurate and collected using appropriate instruments.
- AI-generated findings may be incomplete or incorrect and should be verified before maintenance decisions.
- API availability, usage limits, and optional voice features depend on the relevant service providers.

Future Improvements

- Integration with live solar monitoring sensors.
- Historical performance tracking and anomaly detection.
- Automated comparison of expected and measured power output.
- Detection of visible panel defects using a dedicated computer vision model.
- Maintenance alerts and inspection history.
- Support for multiple solar installations through a centralized dashboard.

Project Vision

SolarSentry aims to make solar inspection more accessible by combining AI-assisted visual analysis, electrical performance data, and actionable reporting in a single application.

Built with Python, Streamlit, and AI APIs.

---

Note: SolarSentry is an evolving prototype. Features and reliability may change as development continues.
