class OpportunityDetector:

    def detect(self, lead):

        text = (
            f"{lead.get('title', '')} "
            f"{lead.get('description', '')}"
        ).lower()

        result = {
            "opportunity": "General Software Development",
            "reason": "General software-related requirement detected.",
            "outreach_strategy": "Introduce LeadFlow AI services.",
            "recommended_services": []
        }

        if any(word in text for word in ["website", "landing page", "frontend"]):
            result["opportunity"] = "Website Development"
            result["recommended_services"] = [
                "Website Development",
                "UI/UX Design"
            ]
            result["reason"] = "The lead appears to require a website or frontend solution."
            result["outreach_strategy"] = (
                "Offer a modern responsive website with SEO optimization."
            )

        elif any(word in text for word in ["dashboard", "analytics", "report"]):
            result["opportunity"] = "Dashboard Development"
            result["recommended_services"] = [
                "Dashboard",
                "Power BI",
                "Admin Panel"
            ]
            result["reason"] = "The lead indicates a reporting or dashboard requirement."
            result["outreach_strategy"] = (
                "Demonstrate a custom analytics dashboard."
            )

        elif any(word in text for word in ["api", "integration"]):
            result["opportunity"] = "API Integration"
            result["recommended_services"] = [
                "REST API",
                "Automation",
                "Integration"
            ]
            result["reason"] = "Integration or API-related work detected."
            result["outreach_strategy"] = (
                "Offer secure API integration and automation services."
            )

        elif any(word in text for word in ["ai", "llm", "chatbot"]):
            result["opportunity"] = "AI Automation"
            result["recommended_services"] = [
                "AI Chatbot",
                "RAG",
                "Workflow Automation"
            ]
            result["reason"] = "The lead mentions AI-related technologies."
            result["outreach_strategy"] = (
                "Propose an AI-powered assistant or automation workflow."
            )

        return result