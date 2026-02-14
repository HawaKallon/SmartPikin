# import os
#
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.generic.edit import CreateView
# from ai_core.models import ReportCardImage
# from account.forms import ReportCardForm
# import base64
# import io
# from PIL import Image
# from transformers import CLIPProcessor, CLIPModel
# from groq import Groq
# import torch
# os.environ["GROQ_API_KEY"] = "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"
#
# # Initialize CLIP and Groq
# clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
# clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
# groq_client = Groq()
#
# # Function to get image embedding
# def get_image_embedding(image):
#     inputs = clip_processor(images=image, return_tensors="pt", padding=True, truncation=True)
#     with torch.no_grad():
#         outputs = clip_model.get_image_features(**inputs)
#     return outputs.squeeze().numpy()
#
# class ReportCardUploadView(CreateView):
#     model = ReportCardImage
#     form_class = ReportCardForm
#     template_name = 'ai_core/upload_image.html'
#     success_url = ''  # Redirect to the same page or another success page
#
#     def form_valid(self, form):
#         # Save the form and image
#         report_card = form.save()
#
#         # Get the uploaded image and process it
#         image_path = report_card.image.path
#         image = Image.open(image_path).convert("RGB")
#
#         # Get the image embedding
#         embedding = get_image_embedding(image)
#
#         # Convert image to base64 for API request
#         image_bytes = io.BytesIO()
#         image.save(image_bytes, format='PNG')
#         base64_image = base64.b64encode(image_bytes.getvalue()).decode('ascii')
#
#         # Generate image description using Groq
#         chat_completion = groq_client.chat.completions.create(
#             model="llama-3.2-11b-vision-preview",
#             messages=[{
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": "Analyze the report card in this image."},
#                     {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
#                 ]
#             }]
#         )
#
#         image_description = chat_completion.choices[0].message.content
#
#         # Return the analysis in the response
#         return JsonResponse({
#             'image_description': image_description,
#             'uploaded_image': f"data:image/png;base64,{base64_image}"
#         })
# import os
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.generic.edit import CreateView
# from ai_core.models import ReportCardImage
# from account.forms import ReportCardForm
# import base64
# import io
# from PIL import Image
# from transformers import CLIPProcessor, CLIPModel
# from groq import Groq
# import torch
#
# os.environ["GROQ_API_KEY"] = "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"
#
# # Initialize CLIP and Groq
# clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
# clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
# groq_client = Groq()
#
#
# # Function to get image embedding
# def get_image_embedding(image):
#     inputs = clip_processor(images=image, return_tensors="pt", padding=True, truncation=True)
#     with torch.no_grad():
#         outputs = clip_model.get_image_features(**inputs)
#     return outputs.squeeze().numpy()
#
#
# class ReportCardUploadView(CreateView):
#     model = ReportCardImage
#     form_class = ReportCardForm
#     template_name = 'ai_core/upload_image.html'
#     success_url = ''  # Redirect to the same page or another success page
#
#     def form_valid(self, form):
#         # Save the form and image
#         report_card = form.save()
#
#         # Get the uploaded image and process it
#         image_path = report_card.image.path
#         image = Image.open(image_path).convert("RGB")
#
#         # Convert image to base64 for API request
#         image_bytes = io.BytesIO()
#         image.save(image_bytes, format='PNG')
#         base64_image = base64.b64encode(image_bytes.getvalue()).decode('ascii')
#
#         # Generate an enhanced analysis prompt for Groq
#         prompt = """
#         Analyze the report card in this image and extract the following information:
#         1. Student name
#         2. Attendance details
#         3. Scores and grades for each subject
#         4. Comments or remarks (if available)
#         5. Any other significant information such as rank or teacher's comments
#         Provide the extracted information in a structured format, clearly listing each category.
#         """
#
#         # Generate image description using Groq
#         chat_completion = groq_client.chat.completions.create(
#             model="Llama-3.2-11B-Vision-Instruct",
#             messages=[{
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                     {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
#                 ]
#             }]
#         )
#
#         # Extract image description from the response
#         image_description = chat_completion.choices[0].message.content
#
#         # Return the analysis in the response as JSON
#         return JsonResponse({
#             'image_description': image_description,
#
#         })
import base64
import io
import os
import markdown
from PIL import Image
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from ai_core.models import ReportCardImage
from account.forms import ReportCardForm
from groq import Groq

from django.conf import settings
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
groq_client = Groq(api_key=settings.GROQ_API_KEY)


class ReportCardUploadView(LoginRequiredMixin, CreateView):
    model = ReportCardImage
    form_class = ReportCardForm
    template_name = 'ai_core/upload_image.html'
    success_url = ''  # Redirect after successful upload

    def form_valid(self, form):
        # Save the uploaded form and image
        report_card = form.save()

        # Convert image to base64
        image_path = report_card.image.path
        image = Image.open(image_path).convert("RGB")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        base64_image = base64.b64encode(image_bytes.getvalue()).decode('ascii')

        # Prompt for extracting report card details
        prompt = """ 
        Analyze the report card in this image and extract the following information:

1. **Student Name**
2. **Attendance Details**
3. **Scores and Grades for Each Subject** (using the WAEC 2025 Grading System)
4. **Comments or Remarks** (if available)
5. **Any Other Significant Information** (e.g., rank, teacher's comments, or behavioral notes)

**Perform the following analysis:**

1. **Statistical Analysis**:
   - Calculate the average percentage score across all subjects.
   - Identify the student's strongest and weakest subjects based on percentages.
   - Compare the student's performance against the WAEC 2025 grading system (e.g., number of A1s, B2s, C4s, etc.).
   - Provide a breakdown of grades (e.g., Excellent, Very Good, Good, Credit, Pass, Fail).

2. **Career Path Recommendations**:
   - Based on the student's performance, suggest potential career paths aligned with the STEAM (Science, Technology, Engineering, Arts, and Mathematics) educational system.
   - Highlight careers in high-demand fields such as software engineering, data science, renewable energy, biotechnology, and creative industries.
   - Recommend further academic or vocational training programs that align with the student's strengths and interests.

3. **STEAM Alignment**:
   - Identify subjects where the student excels that are relevant to STEAM fields (e.g., Mathematics, Physics, Chemistry, ICT, or Arts).
   - Suggest ways to improve performance in weaker STEAM-related subjects to better prepare for future opportunities in science and technology.

4. **General Recommendations**:
   - Provide actionable advice for the student to improve overall academic performance.
   - Suggest study habits, resources, or extracurricular activities that could enhance their skills and knowledge in STEAM-related areas.

**Output Format**:
Provide the extracted information and analysis in a structured format using Markdown syntax. Include headings, bullet points, and tables where applicable.

---

**Example Output Structure**:

```markdown
# Student Report Card Analysis

## Student Information
- **Name**: [Student Name]
- **Attendance**: [Details]

## Subject Performance
| Subject       | Score (%) | Grade | Remark       |
|---------------|-----------|-------|--------------|
| Mathematics   | 78        | A1    | Excellent    |
| English       | 65        | B3    | Good         |
| Physics       | 72        | B2    | Very Good    |
| Chemistry     | 68        | B3    | Good         |
| ICT           | 80        | A1    | Excellent    |
| ...           | ...       | ...   | ...          |

## Statistical Analysis
- **Average Score**: [X]%
- **Strongest Subject**: [Subject] ([Score]%)
- **Weakest Subject**: [Subject] ([Score]%)
- **Grade Distribution**:
  - A1: [Number]
  - B2: [Number]
  - C4: [Number]
  - D7: [Number]
  - F9: [Number]

## Career Path Recommendations
- **Recommended Careers**: 
  - Software Engineering (strong performance in ICT and Mathematics)
  - Renewable Energy Specialist (strong performance in Physics and Chemistry)
  - Data Scientist (strong performance in Mathematics and ICT)
- **Further Training**: 
  - Enroll in advanced ICT courses.
  - Participate in STEM-focused extracurricular activities.

## STEAM Alignment
- **Strengths**: 
  - Mathematics (78%, A1)
  - ICT (80%, A1)
- **Areas for Improvement**: 
  - Chemistry (68%, B3) – Consider additional tutoring or practical experiments.

## General Recommendations
- Focus on improving weaker subjects through targeted study plans.
- Engage in STEAM-related projects or competitions to build practical skills.
- Utilize online resources (e.g., Khan Academy, Coursera) for additional learning.

## Comments
- [Teacher's Comments or Remarks]
        """

        # Send request to Groq API
        response = groq_client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]
                }
            ]
        )

        # Extract Markdown response and convert to HTML
        markdown_response = response.choices[0].message.content
        formatted_html = markdown.markdown(markdown_response)  # Convert Markdown to HTML

        # Pass the formatted response to the template
        return render(self.request, self.template_name, {"image_description": formatted_html})
