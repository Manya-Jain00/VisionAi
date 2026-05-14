"""
model.py — AI Models for Image Captioning and Visual Question Answering
-----------------------------------------------------------------------
Uses:
  - Salesforce/blip-image-captioning-base  → generates an image caption
  - Salesforce/blip-vqa-base               → answers questions about the image

Both models run entirely on CPU and are downloaded automatically on first run
(~900 MB total). Subsequent runs load from the local HuggingFace cache.
"""

import torch
from transformers import BlipProcessor, BlipForConditionalGeneration, BlipForQuestionAnswering
from PIL import Image


# ──────────────────────────────────────────────────────────
#  ImageAnalyzer
# ──────────────────────────────────────────────────────────

class ImageAnalyzer:
    """Wraps two BLIP models: one for captioning, one for VQA."""

    def __init__(self):
        self.caption_processor = None
        self.caption_model     = None
        self.vqa_processor     = None
        self.vqa_model         = None
        self.device            = "cpu"   # CPU-only; no GPU required
        self.models_loaded     = False

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def load_models(self):
        """Download (first run) and load both BLIP models into memory."""
        if self.models_loaded:
            return   # already loaded — skip

        print("[model] Loading BLIP captioning model …")
        self.caption_processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        self.caption_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        self.caption_model.to(self.device)
        self.caption_model.eval()
        print("[model] Captioning model ready.")

        print("[model] Loading BLIP VQA model …")
        self.vqa_processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-vqa-base"
        )
        self.vqa_model = BlipForQuestionAnswering.from_pretrained(
            "Salesforce/blip-vqa-base"
        )
        self.vqa_model.to(self.device)
        self.vqa_model.eval()
        print("[model] VQA model ready.")

        self.models_loaded = True
        print("[model] ✓ All models loaded successfully.")

    # ------------------------------------------------------------------
    # Captioning
    # ------------------------------------------------------------------

    def generate_caption(self, image: Image.Image) -> str:
        """
        Generate a natural-language caption for *image*.

        Parameters
        ----------
        image : PIL.Image.Image
            The image to describe (RGB mode expected).

        Returns
        -------
        str
            A short descriptive caption, e.g. "a dog sitting on a red couch".
        """
        if not self.models_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")

        # Preprocess the image + run inference
        inputs = self.caption_processor(image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            output = self.caption_model.generate(
                **inputs,
                max_new_tokens=100,     # cap token length
                num_beams=4,            # beam search for better quality
                min_length=5,
            )

        caption = self.caption_processor.decode(output[0], skip_special_tokens=True)
        return caption.strip()

    # ------------------------------------------------------------------
    # Visual Question Answering
    # ------------------------------------------------------------------

    def answer_question(self, image: Image.Image, question: str) -> str:
        """
        Answer *question* about *image* using BLIP-VQA.

        Parameters
        ----------
        image    : PIL.Image.Image
        question : str   — the user's natural-language question

        Returns
        -------
        str
            A short answer extracted from the image content.
        """
        if not self.models_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")

        # Encode image + question together
        inputs = self.vqa_processor(image, question, return_tensors="pt").to(self.device)

        with torch.no_grad():
            output = self.vqa_model.generate(
                **inputs,
                max_new_tokens=50,
                num_beams=4,
            )

        raw_answer = self.vqa_processor.decode(output[0], skip_special_tokens=True)
        return raw_answer.strip()

    # ------------------------------------------------------------------
    # Response polishing
    # ------------------------------------------------------------------

    def build_response(self, raw_answer: str, question: str, caption: str) -> str:
        """
        Convert the bare VQA answer into a natural, readable sentence.

        This simple heuristic layer makes responses feel conversational
        without needing a separate language model.
        """
        q   = question.lower().strip().rstrip("?")
        ans = raw_answer.strip()

        if not ans or ans in ("yes", "no", "unknown", "unanswerable"):
            # Handle yes/no answers
            if ans in ("yes", "no"):
                return f"{ans.capitalize()}."
            # Fallback to caption context
            return (
                f"I'm not entirely sure about that specific detail. "
                f"From the image I can see: {caption}."
            )

        # Tailor the sentence structure to the question type
        if any(q.startswith(p) for p in ("what is", "what are", "what's")):
            return f"It appears to be {ans}."

        if any(p in q for p in ("how many", "count how", "how much")):
            return f"I can count approximately {ans} in the image."

        if q.startswith("where"):
            return f"It looks like {ans}."

        if any(p in q for p in ("who ", "whose ")):
            return f"The person/people appear to be {ans}."

        if any(p in q for p in ("what color", "what colour", "which color", "which colour")):
            return f"The color looks like {ans}."

        if any(p in q for p in ("is there", "are there", "does it", "do you see")):
            return f"{ans.capitalize()}."

        if any(p in q for p in ("describe", "tell me about", "explain", "what can you see")):
            return (
                f"Here is what I observe: {caption}. "
                f"Additionally, {ans}."
            )

        # Generic fallback — still a complete sentence
        return f"{ans.capitalize()}."
