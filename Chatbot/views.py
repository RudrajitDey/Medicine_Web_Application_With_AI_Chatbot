import logging
import markdown

from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET, require_POST

import google.generativeai as genai

from .models import ChatSession, ChatMessage

genai.configure(api_key=settings.GOOGLE_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

system_prompts = {
    "image": """
    You are a domain expert in medical image analysis. You are tasked with
    examining medical images for a renowned hospital. Your expertise will help in identifying
    or discovering any anomalies, diseases, conditions or health issues that might be present in the image.

    Your key responsibilities:
    1. Detailed Analysis: Scrutinize and thoroughly examine each image,
       focusing on finding any abnormalities.
    2. Analysis Report: Document all the findings and
       clearly articulate them in a structured format.
    3. Recommendations: Based on the analysis, suggest remedies,
       tests or treatments as applicable.
    4. Treatments: If applicable, lay out detailed treatments
       which can help in faster recovery.

    Important Notes to remember:
    1. Scope of response: Only respond if the image pertains to human health issues.
    2. Clarity of image: In case the image is unclear,
       note that certain aspects are 'Unable to be correctly determined based on the uploaded image'
    3. Disclaimer: Accompany your analysis with the disclaimer:
       "This is an AI BOT made by MEDI360. Consult with a Doctor before making any decisions."

    Please provide the final response in headings and sub-headings in bullet format:
    Detailed Analysis, Analysis Report, Recommendations and Treatments.

    when you found \\n or \\n\\n in responses extend the output in next line.

    Note: If images are not related to medical topics, as you're a Medical AI Chatbot,
    please inform the user that you can only analyze medical-related images.

    Format the response cleanly using Markdown:
    - Use "###" for main sections
    - Use bullet points (-)
    - Keep each point on a new line
    - Add spacing between sections
    """,
    "text": """
    You are an AI medical assistant designed to provide accurate, safe, and helpful health-related information.

    Your goal is to understand the user's query deeply and respond in the most appropriate way based on the intent.

    -------------------------
     RESPONSE BEHAVIOR
    -------------------------
    - First, identify the type of query:
    (symptoms / disease / medicine / emergency / general health)

    - Then adapt your response accordingly:
    • Symptoms → explain possible causes + guidance
    • Disease → overview + symptoms + treatment
    • Medicine → usage + precautions + side effects
    • Emergency → prioritize urgency and safety
    • General → simple explanation

    -------------------------
     RESPONSE STYLE (FLEXIBLE)
    -------------------------
    - DO NOT force a fixed format
    - Choose only relevant sections from below:

    Possible sections:
    • Overview
    • Symptoms
    • Causes
    • Medication / Treatment
    • Precautions
    • Home Remedies
    • When to Seek Help

    Use ONLY what is needed for the query

    Format the response cleanly using Markdown:
    - Use "###" for main sections
    - Use bullet points (-)
    - Keep each point on a new line
    - Add spacing between sections

    -------------------------
     SAFETY RULES
    -------------------------
    - Do NOT give confirmed diagnosis
    - Do NOT hallucinate
    - If unsure, say: "I am not fully confident. Please consult a doctor."
    - For serious symptoms → emphasize urgency
    - Never give unsafe or illegal advice

    -------------------------
     STYLE
    -------------------------
    - Keep response clear, short (100–200 words)
    - Use simple language
    - Use bullet points if helpful
    - Be natural, like a helpful medical assistant (not robotic)

    -------------------------
     DISCLAIMER
    -------------------------
    End with:

    "Note: This is AI-generated information by VitaMind. Always consult a healthcare professional before making medical decisions."
    """,
}

logger = logging.getLogger(__name__)

model = genai.GenerativeModel(
    model_name="gemini-3.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
)


def _markdown_to_html(text):
    return markdown.markdown(text, extensions=["extra", "nl2br"])


def _generate_title(text, max_len=48):
    title = (text or 'New Chat').strip().replace('\n', ' ')
    if len(title) > max_len:
        return title[:max_len].rsplit(' ', 1)[0] + '…'
    return title or 'New Chat'


def _get_user_session(user, session_id):
    if not session_id:
        return None
    return get_object_or_404(ChatSession, pk=session_id, user=user)


def _call_text_ai(query):
    prompt = [system_prompts["text"], f"User Query: {query}"]
    try:
        ai_response = model.generate_content(prompt)
        if ai_response and ai_response.text:
            return ai_response.text
    except Exception as exc:
        logger.exception("Text AI generation failed")
        if settings.DEBUG:
            return f"Sorry, the AI service is temporarily unavailable. Error: {exc}"
    return "Sorry, the AI service is temporarily unavailable. Please try again later."


def _call_image_ai(image_bytes, mime_type='image/jpeg'):
    image_parts = [{"mime_type": mime_type, "data": image_bytes}]
    prompt = [image_parts[0], system_prompts["image"]]
    try:
        ai_response = model.generate_content(prompt)
        if ai_response and ai_response.text:
            return ai_response.text
    except Exception as exc:
        logger.exception("Image AI generation failed")
        if settings.DEBUG:
            return f"Sorry, the AI service is temporarily unavailable. Error: {exc}"
    return "Sorry, the AI service is temporarily unavailable. Please try again later."


def _session_to_dict(session):
    return {
        'id': session.id,
        'title': session.title,
        'chat_type': session.chat_type,
        'updated_at': session.updated_at.strftime('%b %d, %Y'),
    }


def _message_to_dict(msg):
    data = {
        'id': msg.id,
        'role': msg.role,
        'content': msg.content,
        'created_at': msg.created_at.strftime('%I:%M %p'),
    }
    if msg.image:
        data['image_url'] = msg.image.url
    return data


def chatbot(request):
    sessions = []
    if request.user.is_authenticated:
        sessions = ChatSession.objects.filter(user=request.user)[:80]
    context = {
        'sessions': sessions,
        'is_authenticated': request.user.is_authenticated,
        'login_url': settings.LOGIN_URL,
    }
    return render(request, 'chatAi/medical_ai.html', context)


@login_required(login_url='login')
@require_GET
def list_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user)
    return JsonResponse({
        'sessions': [_session_to_dict(s) for s in sessions],
    })


@login_required(login_url='login')
@require_GET
def get_session(request, session_id):
    session = _get_user_session(request.user, session_id)
    messages = session.messages.all()
    return JsonResponse({
        'session': _session_to_dict(session),
        'messages': [_message_to_dict(m) for m in messages],
    })


@login_required(login_url='login')
@require_POST
def delete_session(request, session_id):
    session = _get_user_session(request.user, session_id)
    session.delete()
    return JsonResponse({'success': True})


@require_POST
def send_message(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'error': 'login_required',
            'message': 'Please log in to save and view your chat history.',
        }, status=401)

    session_id = request.POST.get('session_id')
    query = (request.POST.get('query') or '').strip()
    uploaded = request.FILES.get('image')

    if not query and not uploaded:
        return JsonResponse({'error': 'empty', 'message': 'Please enter a message or upload an image.'}, status=400)

    try:
        session = _get_user_session(request.user, session_id) if session_id else None

        image_url = None
        if uploaded:
            chat_type = 'image'
            user_text = query or 'Medical image analysis'
            image_bytes = uploaded.read()
            mime_type = uploaded.content_type or 'image/jpeg'
            raw_response = _call_image_ai(image_bytes, mime_type)
        else:
            chat_type = 'text'
            user_text = query
            raw_response = _call_text_ai(query)

        html_response = _markdown_to_html(raw_response)

        if not session:
            session = ChatSession.objects.create(
                user=request.user,
                title=_generate_title(user_text),
                chat_type=chat_type,
            )
        elif session.title == 'New Chat':
            session.title = _generate_title(user_text)
            session.chat_type = chat_type
            session.save(update_fields=['title', 'chat_type', 'updated_at'])
        else:
            session.save(update_fields=['updated_at'])

        user_msg = ChatMessage(session=session, role='user', content=user_text)
        if uploaded:
            user_msg.image.save(uploaded.name, ContentFile(image_bytes), save=False)
        user_msg.save()
        if user_msg.image:
            image_url = user_msg.image.url

        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=html_response,
        )

        user_data = _message_to_dict(user_msg)
        if image_url:
            user_data['image_url'] = image_url

        return JsonResponse({
            'session': _session_to_dict(session),
            'user_message': user_data,
            'assistant_message': {
                'role': 'assistant',
                'content': html_response,
            },
        })
    except Exception as exc:
        logger.exception("Error processing chatbot message")
        return JsonResponse({
            'error': 'server_error',
            'message': 'Unable to process your question right now. Please try again later.',
        }, status=500)
