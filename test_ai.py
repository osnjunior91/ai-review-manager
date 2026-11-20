from app.services.ai_analysis_service import AIAnalysisService

service = AIAnalysisService()

result = service.analyze(
    "O açaí estava delicioso, mas demorou muito para chegar!"
)

print("Resposta:", result.content)
print("Modelo:", result.model)
print("Input tokens:", result.input_tokens)
print("Output tokens:", result.output_tokens)
print("Total tokens:", result.total_tokens)