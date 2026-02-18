import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from groq import Groq

from ai_core.models import FlashcardSet
from core.models import ClassLevel

logger = logging.getLogger(__name__)
groq_client = Groq(api_key=settings.GROQ_API_KEY)


class FlashcardGeneratorView(LoginRequiredMixin, View):
    template_name = 'ai_core/flashcard_generator.html'

    def get(self, request):
        return render(request, self.template_name, {
            'class_levels': ClassLevel.choices,
        })

    def post(self, request):
        topic = request.POST.get('topic', '').strip()
        level = request.POST.get('level', '')
        num_cards = int(request.POST.get('num_cards', 5))

        if not topic:
            messages.error(request, "Please enter a topic.")
            return render(request, self.template_name, {
                'class_levels': ClassLevel.choices,
            })

        cards = self.generate_flashcards(topic, level, num_cards)

        if cards is None:
            messages.error(request, "Failed to generate flashcards. Please try again.")
            return render(request, self.template_name, {
                'class_levels': ClassLevel.choices,
            })

        FlashcardSet.objects.create(
            user=request.user,
            topic=topic,
            level=level,
            cards=cards,
            total_cards=len(cards),
        )

        return render(request, self.template_name, {
            'class_levels': ClassLevel.choices,
            'cards_data': cards,
            'topic': topic,
            'level': level,
            'num_cards': len(cards),
        })

    def generate_flashcards(self, topic, level, num_cards):
        prompt = (
            f"Generate exactly {num_cards} study flashcards about {topic} for {level} students "
            f"in Sierra Leone.\n"
            f"Return ONLY valid JSON (no markdown, no explanation, no code fences) in this format:\n"
            f'[{{"front": "question or concept", "back": "clear, concise answer or explanation"}}]\n'
            f"Make the content educational and appropriate for the level."
        )

        for attempt in range(2):
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                content = response.choices[0].message.content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                cards = json.loads(content)
                if isinstance(cards, list) and len(cards) > 0:
                    return cards
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Flashcard generation attempt {attempt + 1} failed: {e}")
                continue

        return None
