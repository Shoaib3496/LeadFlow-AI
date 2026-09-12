import ollama
import json
import re

from config.settings import OLLAMA_MODEL


def _clean_text(value):
    """Convert a value into safe plain text for the prompt."""
    if value is None:
        return ""

    return str(value).strip()


def _clean_generated_message(message, company_name):
    """
    Remove common placeholder artifacts without changing
    the actual meaning of the generated message.
    """
    message = _clean_text(message)

    if not message:
        return message

    company_name = _clean_text(company_name)

    if company_name:
        message = message.replace(
            f"[{company_name}]",
            company_name
        )

        message = message.replace(
            f"{{{company_name}}}",
            company_name
        )

    # Remove common generic placeholder artifacts.
    message = re.sub(
        r"\[(?:Company Name|company name|Company|company)\]",
        company_name or "",
        message,
        flags=re.IGNORECASE
    )

    # Remove personal/signature placeholders.
    message = re.sub(
        r"\[(?:Your Name|your name|Name|name)\]",
        "",
        message,
        flags=re.IGNORECASE
    )

    message = re.sub(
        r"\{(?:Your Name|your name|Name|name)\}",
        "",
        message,
        flags=re.IGNORECASE
    )

    # Remove accidental double spaces.
    message = re.sub(r"[ \t]{2,}", " ", message)

    return message.strip()


def _clean_generated_strategy(strategy):
    """
    Clean the generated outreach strategy while preserving
    its useful structure and meaning.
    """
    strategy = _clean_text(strategy)

    if not strategy:
        return strategy

    # Remove common placeholder artifacts.
    strategy = re.sub(
        r"\[(?:Company Name|company name|Company|company)\]",
        "",
        strategy,
        flags=re.IGNORECASE
    )

    strategy = re.sub(
        r"\[(?:Name|name|Your Name|your name|your company|Your Company)\]",
        "",
        strategy,
        flags=re.IGNORECASE
    )

    # Remove curly-brace placeholders too.
    strategy = re.sub(
        r"\{(?:Company Name|company name|Company|company)\}",
        "",
        strategy,
        flags=re.IGNORECASE
    )

    strategy = re.sub(
        r"\{(?:Name|name|Your Name|your name|your company|Your Company)\}",
        "",
        strategy,
        flags=re.IGNORECASE
    )

    # Clean extra spaces created by removing placeholders.
    strategy = re.sub(r"[ \t]{2,}", " ", strategy)

    return strategy.strip()


def _fallback_outreach(lead):
    """
    Safe fallback that uses only information supplied
    by the lead.
    """
    title = _clean_text(
        lead.get("title")
    )

    company_name = _clean_text(
        lead.get("company_name")
    )

    service = _clean_text(
        lead.get("service_needed")
    )

    technology = _clean_text(
        lead.get("technology")
    )

    if company_name:
        greeting = f"Hi {company_name},"
    else:
        greeting = "Hi,"

    if title:
        project_text = (
            f'I came across your requirement for "{title}".'
        )
    elif service:
        project_text = (
            f"I came across your requirement for "
            f"{service}."
        )
    else:
        project_text = (
            "I came across your project requirement."
        )

    message = (
        f"{greeting}\n\n"
        f"{project_text} "
        "I'd be interested in understanding the "
        "requirements and discussing whether we could "
        "help with the project.\n\n"
        "If you're still evaluating options, "
        "I'd be happy to discuss the details.\n\n"
        "Best regards"
    )

    strategy_parts = [
        "Recommended Approach: Start by acknowledging "
        "the specific project requirement and keep the "
        "conversation focused on the stated need."
    ]

    if service:
        strategy_parts.append(
            f"Key Focus: Discuss the {service} requirement."
        )

    if technology:
        strategy_parts.append(
            f"Technical Focus: Discuss the stated "
            f"{technology} requirement."
        )

    strategy_parts.append(
        "Call to Action: Ask about the current "
        "requirements, timeline, and next steps."
    )

    strategy = "\n\n".join(strategy_parts)

    return {
        "strategy": strategy,
        "subject": "Project Discussion",
        "message": message
    }


def generate_outreach(lead):
    """
    Generate a lead-specific outreach strategy,
    subject, and personalized outreach message.

    Only facts explicitly supplied by the lead may be used.
    """

    company_name = _clean_text(
        lead.get("company_name")
    )

    title = _clean_text(
        lead.get("title")
    )

    description = _clean_text(
        lead.get("description")
    )

    service_needed = _clean_text(
        lead.get("service_needed")
    )

    technology = _clean_text(
        lead.get("technology")
    )

    industry = _clean_text(
        lead.get("industry")
    )

    country = _clean_text(
        lead.get("country")
    )

    website = _clean_text(
        lead.get("website")
    )

    budget = _clean_text(
        lead.get("budget")
    )

    urgency = _clean_text(
        lead.get("urgency")
    )

    buyer_intent_score = _clean_text(
        lead.get("buyer_intent_score")
    )

    business_fit_score = _clean_text(
        lead.get("business_fit_score")
    )

    commercial_score = _clean_text(
        lead.get("commercial_score")
    )

    commercial_priority = _clean_text(
        lead.get("commercial_priority")
    )

    ranking_reason = _clean_text(
        lead.get("ranking_reason")
    )

    prompt = f"""
You are a professional B2B sales strategist.

Analyze the specific business opportunity below and create:

1. A practical outreach strategy for this specific lead.
2. A short relevant email subject.
3. A personalized outreach message.

IMPORTANT:

The outreach strategy must be specific to THIS lead.

Do not create a generic strategy that could apply to every lead.

Use the lead's actual:
- project requirement
- description
- service needed
- technology
- company
- industry
- budget
- urgency
- buyer intent
- business fit
- commercial score
- priority
- ranking reason

STRICT FACTUAL RULES:

- Use ONLY information explicitly provided below.
- NEVER invent previous clients.
- NEVER claim previous work with the company.
- NEVER invent experience.
- NEVER invent expertise.
- NEVER invent achievements.
- NEVER invent results.
- NEVER invent revenue.
- NEVER invent customers.
- NEVER invent certifications.
- NEVER invent case studies.
- NEVER invent technologies.
- NEVER invent a company representative's name.
- NEVER invent a budget.
- NEVER make claims about RARS INNOVENTA that are not provided.
- Do not use square brackets as placeholders.
- Do not write "[Company Name]", "[Name]", or similar placeholders.
- If company information is available, use it naturally.
- If company information is missing, do not invent it.
- Mention the actual project requirement when possible.
- Keep the strategy practical and actionable.
- Keep the message professional, natural, and human.
- Avoid spam-style language.
- Do not use exaggerated claims.
- Keep the outreach message around 60-100 words.
- Include a clear but low-pressure call to action.
- Return ONLY valid JSON.

OUTREACH STRATEGY REQUIREMENTS:

Create a concise strategy containing:

Recommended Approach:
How the prospect should be approached based on this lead.

Key Talking Points:
The most relevant points to discuss based only on the lead data.

Recommended CTA:
A realistic low-pressure next step.

Tone:
The appropriate communication tone for this particular lead.

Avoid:
What should be avoided when contacting this lead.

The strategy should normally be around 80-150 words.

LEAD DETAILS:

Title:
{title or "Not provided"}

Description:
{description or "Not provided"}

Business Type:
{_clean_text(lead.get("business_type")) or "Not provided"}

Service Needed:
{service_needed or "Not provided"}

Technology:
{technology or "Not provided"}

Company:
{company_name or "Not provided"}

Industry:
{industry or "Not provided"}

Country:
{country or "Not provided"}

Website:
{website or "Not provided"}

Budget:
{budget or "Not provided"}

Urgency:
{urgency or "Not provided"}

Buyer Intent:
{buyer_intent_score or "Not provided"}/100

Business Fit:
{business_fit_score or "Not provided"}/100

Commercial Score:
{commercial_score or "Not provided"}/100

Priority:
{commercial_priority or "Not provided"}

Ranking Reason:
{ranking_reason or "Not provided"}

Return exactly this JSON structure:

{{
    "strategy": "Recommended Approach: ...\\n\\nKey Talking Points: ...\\n\\nRecommended CTA: ...\\n\\nTone: ...\\n\\nAvoid: ...",
    "subject": "Short relevant subject",
    "message": "Personalized outreach message"
}}
"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response["message"]["content"]

        # Remove markdown code fences.
        result = result.replace("```json", "")
        result = result.replace("```", "")

        # Extract JSON object.
        start = result.find("{")
        end = result.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                "Ollama response did not contain valid JSON."
            )

        result = result[start:end + 1]

        parsed = json.loads(result, strict=False)

        strategy = _clean_text(
            parsed.get("strategy")
        )

        subject = _clean_text(
            parsed.get("subject")
        )

        message = _clean_text(
            parsed.get("message")
        )

        if not strategy:
            raise ValueError(
                "Ollama returned an empty outreach strategy."
            )

        if not subject:
            subject = "Project Discussion"

        if not message:
            raise ValueError(
                "Ollama returned an empty outreach message."
            )

        strategy = _clean_generated_strategy(
            strategy
        )

        message = _clean_generated_message(
            message,
            company_name
        )

        # Reject common hallucinated claims and placeholders.
        unsafe_patterns = [
            r"\bour team has expertise\b",
            r"\bour team specializes\b",
            r"\bwe have helped\b",
            r"\bwe've helped\b",
            r"\bwe have worked with\b",
            r"\bwe've worked with\b",
            r"\bour clients\b",
            r"\bour previous work\b",
            r"\bprevious clients\b",
            r"\bprofessional web development services provider\b",
            r"\bprofessional web developer\b",
            r"\bweb development expert\b",
            r"\bwith our expertise\b",
            r"\bour expertise\b",
            r"\bwe specialize\b",
            r"\bour team specializes\b",
        ]

        for pattern in unsafe_patterns:
            if re.search(
                pattern,
                message,
                flags=re.IGNORECASE
            ):
                raise ValueError(
                    "Unsafe or unsupported outreach claim "
                    f"detected: {pattern}"
                )

        return {
            "strategy": strategy,
            "subject": subject,
            "message": message
        }

    except Exception as e:
        print(
            "Outreach generation failed:",
            type(e).__name__,
            str(e)
        )

        return _fallback_outreach(lead)