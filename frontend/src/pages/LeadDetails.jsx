import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import { toast } from "react-toastify";

function LeadDetails() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [lead, setLead] = useState(null);
    const [loading, setLoading] = useState(true);
    const [savingStatus, setSavingStatus] = useState(false);
    const [savingDealValue, setSavingDealValue] = useState(false);

    const [generatingOutreach, setGeneratingOutreach] = useState(false);
    const [outreachSubject, setOutreachSubject] = useState("");
    const [outreachMessage, setOutreachMessage] = useState("");

    useEffect(() => {
        async function loadLead() {
            try {
                setLoading(true);

                const response = await api.get(`/lead/${id}`);

                setLead(response.data);

                if (response.data.outreach_message) {
                    try {
                        const outreach =
                            typeof response.data.outreach_message === "string"
                                ? JSON.parse(response.data.outreach_message)
                                : response.data.outreach_message;

                        setOutreachSubject(outreach.subject || "");
                        setOutreachMessage(outreach.message || "");
                    } catch (error) {
                        console.error("Failed to parse outreach message:", error);
                        setOutreachSubject("");
                        setOutreachMessage("");
                    }
                } else {
                    setOutreachSubject("");
                    setOutreachMessage("");
                }
            } catch (error) {
                console.error("Failed to load lead:", error);
                toast.error("Failed to load lead details.");
            } finally {
                setLoading(false);
            }
        }

        loadLead();
    }, [id]);

    const updateStatus = async () => {
        if (!lead) return;

        try {
            setSavingStatus(true);

            const formData = new FormData();

            formData.append(
                "crm_status",
                lead.crm_status || "New"
            );

            const response = await api.post(
                `/lead/${lead.id}/status`,
                formData
            );

            if (!response.data?.success) {
                throw new Error("Lead status was not saved");
            }

            const refreshed = await api.get(
                `/lead/${lead.id}`
            );

            setLead(refreshed.data);

            toast.success(
                "Lead status updated successfully!"
            );
        } catch (error) {
            console.error(
                "Failed to update status:",
                error
            );

            toast.error(
                "Failed to update lead status."
            );
        } finally {
            setSavingStatus(false);
        }
    };

    const updateCRMState = async (changes) => {
        if (!lead) return;

        try {
            const response = await api.patch(
                `/lead/${lead.id}/crm-state`,
                changes
            );

            if (!response.data?.success) {
                throw new Error(
                    "CRM information was not saved"
                );
            }

            const refreshed = await api.get(
                `/lead/${lead.id}`
            );

            setLead(refreshed.data);

            toast.success(
                "CRM information updated successfully!"
            );
        } catch (error) {
            console.error(
                "Failed to update CRM information:",
                error
            );

            toast.error(
                "Failed to update CRM information."
            );
        }
    };

    const markAsContacted = async () => {
        if (!lead) return;

        try {
            const formData = new FormData();
            formData.append("crm_status", "Contacted");

            const response = await api.post(
                `/lead/${lead.id}/status`,
                formData
            );

            if (!response.data?.success) {
                throw new Error("Failed to mark lead as contacted");
            }

            const leadResponse = await api.get(
                `/lead/${lead.id}`
            );

            setLead(leadResponse.data);

            toast.success("Lead marked as contacted!");

        } catch (error) {
            console.error(
                "Failed to mark lead as contacted:",
                error
            );

            toast.error(
                "Failed to mark lead as contacted."
            );
        }
    };

    const saveDealValue = async () => {
        if (!lead) return;

        try {
            setSavingDealValue(true);

            const value = Number(lead.deal_value);

            if (!Number.isFinite(value) || value < 0) {
                toast.error("Please enter a valid deal value.");
                return;
            }

            const formData = new FormData();

            formData.append(
                "deal_value",
                String(value)
            );

            const response = await api.post(
                `/lead/${lead.id}/deal-value`,
                formData
            );

            if (!response.data?.success) {
                throw new Error(
                    response.data?.message ||
                    "Failed to save deal value"
                );
            }

            setLead({
                ...lead,
                deal_value: response.data.deal_value
            });

            toast.success(
                "Deal value saved successfully!"
            );

        } catch (error) {
            console.error(
                "Failed to save deal value:",
                error
            );

            toast.error(
                "Failed to save deal value."
            );

        } finally {
            setSavingDealValue(false);
        }
    };

    const contactViaEmail = async () => {
        if (!lead?.email) {
            toast.error("No email address available for this lead.");
            return;
        }

        try {
            const formData = new FormData();

            formData.append("crm_status", "Contacted");

            const response = await api.post(
                `/lead/${lead.id}/status`,
                formData
            );

            if (!response.data?.success) {
                throw new Error("Failed to mark lead as contacted");
            }

            const emailSubject = outreachSubject?.trim()
                || `Regarding: ${lead.title}`;

            const emailBody = outreachMessage?.trim() || "";

            const mailtoUrl =
                `mailto:${lead.email}` +
                `?subject=${encodeURIComponent(emailSubject)}` +
                `&body=${encodeURIComponent(emailBody)}`;

            // Open the user's email client.
            window.location.href = mailtoUrl;

            // Refresh lead data so Last Contact is updated.
            const leadResponse = await api.get(
                `/lead/${lead.id}`
            );

            setLead(leadResponse.data);

            toast.success(
                "Lead marked as contacted!"
            );

        } catch (error) {
            console.error(
                "Failed to contact lead:",
                error
            );

            toast.error(
                "Failed to mark lead as contacted."
            );
        }
    };

    const generateOutreach = async () => {
        if (!lead) return;

        try {
            setGeneratingOutreach(true);

            const response = await api.post(
                `/lead/${lead.id}/generate-outreach`
            );

            if (!response.data?.success) {
                throw new Error("Outreach generation failed");
            }

            setOutreachSubject(
                response.data.subject || ""
            );

            setOutreachMessage(
                response.data.message || ""
            );

            setLead({
                ...lead,
                outreach_strategy:
                    response.data.strategy || "",
                outreach_message: JSON.stringify({
                    subject:
                        response.data.subject || "",
                    message:
                        response.data.message || ""
                })
            });

            toast.success(
                "AI outreach strategy and message generated!"
            );

        } catch (error) {
            console.error(
                "Failed to generate outreach:",
                error
            );

            toast.error(
                "Failed to generate AI outreach."
            );

        } finally {
            setGeneratingOutreach(false);
        }
    };

    const saveOutreach = async () => {
        if (!lead) return;

        if (!outreachSubject.trim() || !outreachMessage.trim()) {
            toast.error("Subject and message cannot be empty.");
            return;
        }

        try {
            const formData = new FormData();

            formData.append(
                "subject",
                outreachSubject.trim()
            );

            formData.append(
                "message",
                outreachMessage.trim()
            );

            const response = await api.post(
                `/lead/${lead.id}/outreach`,
                formData
            );

            if (!response.data?.success) {
                throw new Error("Failed to save outreach");
            }

            setLead({
                ...lead,
                outreach_message: JSON.stringify({
                    subject: response.data.subject,
                    message: response.data.message
                })
            });

            setOutreachSubject(
                response.data.subject || ""
            );

            setOutreachMessage(
                response.data.message || ""
            );

            toast.success(
                "Outreach message saved successfully!"
            );

        } catch (error) {
            console.error(
                "Failed to save outreach:",
                error
            );

            toast.error(
                "Failed to save outreach message."
            );
        }
    };

    const isContactDisabled = ["CLOSED", "EXPIRED", "REMOVED"].includes(
        lead?.opportunity_status
    );

    const getStatusBadge = (status) => {
        switch (status) {
            case "New":
                return "bg-green-100 text-green-700 border-green-200";

            case "Contacted":
                return "bg-blue-100 text-blue-700 border-blue-200";

            case "Meeting Scheduled":
                return "bg-purple-100 text-purple-700 border-purple-200";

            case "Proposal Sent":
                return "bg-yellow-100 text-yellow-700 border-yellow-200";

            case "Won":
                return "bg-emerald-100 text-emerald-700 border-emerald-200";

            case "Lost":
                return "bg-red-100 text-red-700 border-red-200";

            default:
                return "bg-gray-100 text-gray-700 border-gray-200";
        }
    };

    const getScoreColor = (score) => {
        if (score === null || score === undefined) {
            return "text-gray-400";
        }

        if (score >= 80) return "text-green-600";
        if (score >= 60) return "text-blue-600";
        if (score >= 40) return "text-orange-500";

        return "text-red-600";
    };

    const getScoreBackground = (score) => {
        if (score === null || score === undefined) {
            return "bg-gray-100";
        }

        if (score >= 80) return "bg-green-50 border-green-200";
        if (score >= 60) return "bg-blue-50 border-blue-200";
        if (score >= 40) return "bg-orange-50 border-orange-200";

        return "bg-red-50 border-red-200";
    };

    const formatScore = (score) => {
        if (score === null || score === undefined || score === "") {
            return "—";
        }

        return score;
    };

    const formatDate = (value) => {
        if (!value) return "—";

        try {
            return new Date(value).toLocaleString();
        } catch {
            return value;
        }
    };

    const InfoRow = ({ label, value, children }) => (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-gray-200 pb-3">
            <span className="font-medium text-gray-500">
                {label}
            </span>

            <span className="text-gray-900 sm:text-right break-words">
                {children !== undefined ? children : value || "—"}
            </span>
        </div>
    );

    const ScoreCard = ({ title, score, icon }) => (
        <div
            className={`rounded-2xl border p-5 ${getScoreBackground(score)}`}
        >
            <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-gray-700">
                    {title}
                </span>

                <span className="text-xl">
                    {icon}
                </span>
            </div>

            <div className={`text-3xl font-bold ${getScoreColor(score)}`}>
                {formatScore(score)}
            </div>

            <div className="text-xs text-gray-500 mt-1">
                AI assessment
            </div>
        </div>
    );

    if (loading) {
        return (
            <div className="flex justify-center items-center h-96">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto"></div>

                    <p className="mt-4 text-gray-600 font-medium">
                        Loading Lead Details...
                    </p>
                </div>
            </div>
        );
    }

    if (!lead) {
        return (
            <div className="max-w-4xl mx-auto py-16 text-center">
                <div className="bg-white rounded-2xl shadow border border-gray-200 p-10">
                    <div className="text-5xl mb-4">
                        🔍
                    </div>

                    <h2 className="text-2xl font-bold text-gray-800">
                        Lead not found
                    </h2>

                    <p className="text-gray-500 mt-2">
                        The requested lead could not be loaded.
                    </p>

                    <button
                        onClick={() => navigate(-1)}
                        className="mt-6 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold"
                    >
                        ← Go Back
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto space-y-6 pb-10">

            {/* =====================================================
                HEADER
            ====================================================== */}

            <div className="flex flex-col gap-5">

                <button
                    onClick={() => navigate(-1)}
                    className="self-start flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold transition"
                >
                    ← Back to Leads
                </button>

                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">

                    <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">

                        <div className="min-w-0">

                            <div className="flex flex-wrap items-center gap-2 mb-4">

                                <span className="bg-blue-100 text-blue-700 px-3 py-1.5 rounded-full text-sm font-semibold">
                                    {lead.platform || "Unknown Source"}
                                </span>

                                <span
                                    className={`px-3 py-1.5 rounded-full text-sm font-semibold border ${getStatusBadge(
                                        lead.crm_status
                                    )}`}
                                >
                                    {lead.crm_status || "New"}
                                </span>

                                <span className="bg-purple-100 text-purple-700 px-3 py-1.5 rounded-full text-sm font-semibold">
                                    {lead.business_type || "Business"}
                                </span>

                            </div>

                            <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 leading-tight">
                                {lead.title || "Untitled Lead"}
                            </h1>

                            <p className="text-gray-500 mt-3">
                                Review, qualify and manage this business opportunity.
                            </p>

                        </div>

                        {/* Overall Score */}

                        <div
                            className={`flex-shrink-0 rounded-2xl border p-5 text-center min-w-[150px] ${getScoreBackground(
                                lead.lead_score
                            )}`}
                        >
                            <div className="text-sm font-semibold text-gray-500">
                                Lead Score
                            </div>

                            <div
                                className={`text-4xl font-bold mt-1 ${getScoreColor(
                                    lead.lead_score
                                )}`}
                            >
                                {formatScore(lead.lead_score)}
                            </div>

                            <div className="text-xs text-gray-500 mt-1">
                                Overall AI score
                            </div>
                        </div>

                    </div>
                </div>
            </div>


            {/* =====================================================
                AI INTELLIGENCE
            ====================================================== */}

            <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">

                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">

                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">
                            🤖 AI Intelligence
                        </h2>

                        <p className="text-gray-500 mt-1">
                            AI-generated qualification and commercial assessment.
                        </p>
                    </div>

                    <span className="text-sm bg-gray-100 text-gray-600 px-3 py-2 rounded-lg">
                        AI Scoring
                    </span>

                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">

                    <ScoreCard
                        title="Buyer Intent"
                        score={lead.buyer_intent_score}
                        icon="🎯"
                    />

                    <ScoreCard
                        title="Business Fit"
                        score={lead.business_fit_score}
                        icon="🏢"
                    />

                    <ScoreCard
                        title="Qualification"
                        score={lead.qualification_score}
                        icon="✅"
                    />

                    <ScoreCard
                        title="Commercial"
                        score={lead.commercial_score}
                        icon="💰"
                    />

                    <ScoreCard
                        title="Priority"
                        score={lead.priority_score}
                        icon="🔥"
                    />

                </div>

                <div className="mt-5 grid grid-cols-1 lg:grid-cols-2 gap-5">

                    <div className="bg-gray-50 rounded-2xl p-5">

                        <h3 className="font-bold text-gray-800 mb-3">
                            Ranking Reason
                        </h3>

                        <p className="text-gray-600 leading-7">
                            {lead.ranking_reason ||
                                "No ranking reason available."}
                        </p>

                    </div>

                    <div className="bg-gray-50 rounded-2xl p-5">

                        <h3 className="font-bold text-gray-800 mb-3">
                            Commercial Priority
                        </h3>

                        <p className="text-gray-600 leading-7">
                            {lead.commercial_priority || "—"}
                        </p>

                    </div>

                </div>

            </section>


            {/* =====================================================
                LEAD + PROJECT INFORMATION
            ====================================================== */}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">

                    <h2 className="text-xl font-bold text-gray-900 mb-6">
                        📋 Lead Information
                    </h2>

                    <div className="space-y-4">

                        <InfoRow
                            label="Platform"
                            value={lead.platform}
                        />

                        <InfoRow
                            label="Business Type"
                            value={lead.business_type}
                        />

                        <InfoRow
                            label="Lead Category"
                            value={lead.lead_category}
                        />

                        <InfoRow
                            label="Service Needed"
                            value={lead.service_needed}
                        />

                        <InfoRow
                            label="Primary Service"
                            value={lead.primary_service}
                        />

                        <InfoRow
                            label="Technology"
                            value={lead.technology}
                        />

                        <InfoRow
                            label="Company Stage"
                            value={lead.company_stage}
                        />

                        <InfoRow
                            label="Project Type"
                            value={lead.project_type}
                        />

                    </div>

                </section>


                <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">

                    <h2 className="text-xl font-bold text-gray-900 mb-6">
                        💰 Commercial Information
                    </h2>

                    <div className="space-y-4">

                        <InfoRow
                            label="Budget"
                            value={lead.budget}
                        />

                        <InfoRow
                            label="Budget Min"
                            value={lead.budget_min}
                        />

                        <InfoRow
                            label="Budget Max"
                            value={lead.budget_max}
                        />

                        <InfoRow
                            label="Currency"
                            value={lead.currency}
                        />

                        <InfoRow
                            label="Urgency"
                            value={lead.urgency}
                        />

                        <InfoRow
                            label="Bid Count"
                            value={lead.bid_count}
                        />

                        <InfoRow
                            label="Marketplace Urgent"
                            value={
                                lead.marketplace_urgent === true
                                    ? "Yes"
                                    : lead.marketplace_urgent === false
                                        ? "No"
                                        : "—"
                            }
                        />

                        <InfoRow
                            label="Source Confidence"
                            value={
                                lead.source_confidence !== null &&
                                lead.source_confidence !== undefined
                                    ? `${lead.source_confidence}%`
                                    : "—"
                            }
                        />

                    </div>

                </section>

            </div>


            {/* =====================================================
                COMPANY INFORMATION
            ====================================================== */}

            <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">

                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">

                    <div>
                        <h2 className="text-xl font-bold text-gray-900">
                            🏢 Company Information
                        </h2>

                        <p className="text-gray-500 mt-1">
                            Add and manage company and contact information for this lead.
                        </p>
                    </div>

                    <button
                        onClick={async () => {
                            try {
                                const formData = new FormData();

                                formData.append(
                                    "company_name",
                                    lead.company_name || ""
                                );

                                formData.append(
                                    "industry",
                                    lead.industry || ""
                                );

                                formData.append(
                                    "country",
                                    lead.country || ""
                                );

                                formData.append(
                                    "website",
                                    lead.website || ""
                                );

                                formData.append(
                                    "email",
                                    lead.email || ""
                                );

                                formData.append(
                                    "linkedin",
                                    lead.linkedin || ""
                                );

                                const response = await api.post(
                                    `/lead/${lead.id}/company`,
                                    formData
                                );

                                if (!response.data?.success) {
                                    throw new Error(
                                        response.data?.message ||
                                        "Company information was not saved"
                                    );
                                }

                                toast.success(
                                    "Company information saved successfully!"
                                );

                                const refreshed = await api.get(
                                    `/lead/${lead.id}`
                                );

                                setLead(refreshed.data);

                            } catch (error) {
                                console.error(
                                    "Failed to save company information:",
                                    error
                                );

                                toast.error(
                                    "Failed to save company information."
                                );
                            }
                        }}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl font-semibold transition"
                    >
                        Save Company Information
                    </button>

                </div>


                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                    {/* =================================================
                        BASIC COMPANY INFORMATION
                    ================================================== */}

                    <div className="space-y-5">

                        {/* Company */}
                        <div>
                            <label className="font-semibold block mb-2 text-gray-800">
                                Company
                            </label>

                            <input
                                type="text"
                                value={lead.company_name || ""}
                                onChange={(e) =>
                                    setLead({
                                        ...lead,
                                        company_name: e.target.value
                                    })
                                }
                                placeholder="Enter company name"
                                className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            />
                        </div>


                        {/* Industry */}
                        <div>
                            <label className="font-semibold block mb-2 text-gray-800">
                                Industry
                            </label>

                            <input
                                type="text"
                                value={lead.industry || ""}
                                onChange={(e) =>
                                    setLead({
                                        ...lead,
                                        industry: e.target.value
                                    })
                                }
                                placeholder="Enter industry"
                                className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            />
                        </div>


                        {/* Country */}
                        <div>
                            <label className="font-semibold block mb-2 text-gray-800">
                                Country
                            </label>

                            <input
                                type="text"
                                value={lead.country || ""}
                                onChange={(e) =>
                                    setLead({
                                        ...lead,
                                        country: e.target.value
                                    })
                                }
                                placeholder="Enter country"
                                className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            />
                        </div>


                        {/* Company Stage */}
                        <div>
                            <label className="font-semibold block mb-2 text-gray-800">
                                Company Stage
                            </label>

                            <input
                                type="text"
                                value={lead.company_stage || ""}
                                onChange={(e) =>
                                    setLead({
                                        ...lead,
                                        company_stage: e.target.value
                                    })
                                }
                                placeholder="Startup, SMB, Enterprise, etc."
                                className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            />
                        </div>

                    </div>


                    {/* =================================================
                        CONTACT INFORMATION
                    ================================================== */}

                    <div className="space-y-5">

                        {/* Website */}
                        <div>
                            <label className="font-semibold block mb-2 text-gray-800">
                                Website
                            </label>

                            <input
                                type="url"
                                value={lead.website || ""}
                                onChange={(e) =>
                                    setLead({
                                        ...lead,
                                        website: e.target.value
                                    })
                                }
                                placeholder="https://example.com"
                                className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            />

                            {lead.website && (
                                <a
                                    href={lead.website}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="inline-block mt-2 text-blue-600 hover:underline text-sm font-medium"
                                >
                                    Visit Website ↗
                                </a>
                            )}
                        </div>


                        {/* Email */}
                        <div>
                            <label className="font-semibold block mb-2 text-gray-800">
                                Email
                            </label>

                            <input
                                type="email"
                                value={lead.email || ""}
                                onChange={(e) =>
                                    setLead({
                                        ...lead,
                                        email: e.target.value
                                    })
                                }
                                placeholder="contact@example.com"
                                className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            />

                            {lead.email && (
                                <a
                                    href={`mailto:${lead.email}`}
                                    className="inline-block mt-2 text-blue-600 hover:underline text-sm"
                                >
                                    Send Email ↗
                                </a>
                            )}
                        </div>


                        {/* LinkedIn */}
                        <div>
                            <label className="font-semibold block mb-2 text-gray-800">
                                LinkedIn Profile
                            </label>

                            <input
                                type="url"
                                value={lead.linkedin || ""}
                                onChange={(e) =>
                                    setLead({
                                        ...lead,
                                        linkedin: e.target.value
                                    })
                                }
                                placeholder="https://www.linkedin.com/in/profile/"
                                className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            />

                            {lead.linkedin && (
                                <a
                                    href={lead.linkedin}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="inline-block mt-2 text-blue-600 hover:underline text-sm font-medium"
                                >
                                    Open LinkedIn Profile ↗
                                </a>
                            )}
                        </div>

                    </div>

                </div>

            </section>


            {/* =====================================================
                CRM MANAGEMENT
            ====================================================== */}

            <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">

                <div className="mb-6">

                    <h2 className="text-2xl font-bold text-gray-900">
                        🎯 CRM Management
                    </h2>

                    <p className="text-gray-500 mt-1">
                        Manage the current sales stage and CRM information.
                    </p>

                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    {/* Status */}

                    <div className="bg-gray-50 rounded-2xl p-5">

                        <label className="font-semibold block mb-3 text-gray-800">
                            Lead Status
                        </label>

                        <select
                            value={lead.crm_status || "New"}
                            onChange={(e) =>
                                setLead({
                                    ...lead,
                                    crm_status: e.target.value,
                                })
                            }
                            className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        >
                            <option>New</option>
                            <option>Contacted</option>
                            <option>Meeting Scheduled</option>
                            <option>Proposal Sent</option>
                            <option>Won</option>
                            <option>Lost</option>
                        </select>

                        <button
                            onClick={updateStatus}
                            disabled={savingStatus}
                            className="mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-6 py-3 rounded-xl font-semibold transition"
                        >
                            {savingStatus ? "Saving..." : "Save Status"}
                        </button>

                    </div>


                    {/* CRM fields */}

                    <div className="bg-gray-50 rounded-2xl p-5">

                        <h3 className="font-bold text-gray-800 mb-4">
                            CRM Information
                        </h3>

                        <div className="space-y-5">

                            {/* Assigned To */}
                            <div>
                                <label className="font-semibold block mb-2 text-gray-800">
                                    Assigned To
                                </label>

                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        value={lead.assigned_to || ""}
                                        onChange={(e) =>
                                            setLead({
                                                ...lead,
                                                assigned_to: e.target.value
                                            })
                                        }
                                        placeholder="Enter person or team"
                                        className="flex-1 border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                                    />

                                    <button
                                        onClick={async () => {
                                            try {
                                                const formData = new FormData();

                                                formData.append(
                                                    "assigned_to",
                                                    lead.assigned_to || ""
                                                );

                                                const response = await api.post(
                                                    `/lead/${lead.id}/assign`,
                                                    formData,
                                                    {
                                                        headers: {
                                                            "Content-Type": "multipart/form-data",
                                                        },
                                                    }
                                                );

                                                if (!response.data?.success) {
                                                    throw new Error("Assignment was not saved");
                                                }

                                                toast.success(
                                                    "Lead assigned successfully!"
                                                );

                                                // Reload the lead from backend
                                                const refreshed = await api.get(
                                                    `/lead/${lead.id}`
                                                );

                                                setLead(refreshed.data);

                                            } catch (error) {
                                                console.error(
                                                    "Failed to assign lead:",
                                                    error
                                                );

                                                toast.error(
                                                    "Failed to assign lead."
                                                );
                                            }
                                        }}
                                        className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl font-semibold transition"
                                    >
                                        Save
                                    </button>
                                </div>
                            </div>

                            {/* Notes */}
                            <div>
                                <label className="font-semibold block mb-2 text-gray-800">
                                    Notes
                                </label>

                                <textarea
                                    value={lead.notes || ""}
                                    onChange={(e) =>
                                        setLead({
                                            ...lead,
                                            notes: e.target.value
                                        })
                                    }
                                    placeholder="Add notes about this lead..."
                                    rows={4}
                                    className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
                                />

                                <button
                                    onClick={async () => {
                                        try {
                                            const formData = new FormData();

                                            formData.append(
                                                "notes",
                                                lead.notes || ""
                                            );

                                            const response = await api.post(
                                                `/lead/${lead.id}/notes`,
                                                formData,
                                                {
                                                    headers: {
                                                        "Content-Type": "multipart/form-data",
                                                    },
                                                }
                                            );

                                            if (!response.data?.success) {
                                                throw new Error("Notes were not saved");
                                            }

                                            toast.success(
                                                "Notes saved successfully!"
                                            );

                                            const refreshed = await api.get(
                                                `/lead/${lead.id}`
                                            );

                                            setLead(refreshed.data);

                                        } catch (error) {
                                            console.error(
                                                "Failed to save notes:",
                                                error
                                            );

                                            toast.error(
                                                "Failed to save notes."
                                            );
                                        }
                                    }}
                                    className="mt-3 bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl font-semibold transition"
                                >
                                    Save Notes
                                </button>
                            </div>


                            {/* Last Contact */}
                            <div>
                                <label className="font-semibold block mb-2 text-gray-800">
                                    Last Contact
                                </label>

                                <div className="border border-gray-300 rounded-xl px-4 py-3 bg-white text-gray-700">
                                    {formatDate(lead.last_contact_date)}
                                </div>
                            </div>


                            {/* Next Follow-up */}
                            <div>
                                <label className="font-semibold block mb-2 text-gray-800">
                                    Next Follow-up
                                </label>

                                <div className="flex gap-2">
                                    <input
                                        type="datetime-local"
                                        value={
                                            lead.next_followup
                                                ? String(lead.next_followup).slice(0, 16)
                                            : ""
                                        }
                                        onChange={(e) =>
                                            setLead({
                                                ...lead,
                                                next_followup: e.target.value
                                            })
                                        }
                                        className="flex-1 border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                                    />

                                    <button
                                        onClick={async () => {
                                            try {
                                                if (!lead.next_followup) {
                                                    toast.error(
                                                        "Please select a follow-up date."
                                                    );
                                                    return;
                                                }

                                                const formData = new FormData();

                                                formData.append(
                                                    "next_followup",
                                                    lead.next_followup
                                                );

                                                const response = await api.post(
                                                    `/lead/${lead.id}/followup`,
                                                    formData,
                                                    {
                                                        headers: {
                                                            "Content-Type":
                                                                "multipart/form-data",
                                                        },
                                                    }
                                                );

                                                if (!response.data?.success) {
                                                    throw new Error(
                                                        "Follow-up date was not saved"
                                                    );
                                                }

                                                toast.success(
                                                    "Follow-up date saved successfully!"
                                                );

                                                const refreshed = await api.get(
                                                    `/lead/${lead.id}`
                                                );

                                                setLead(refreshed.data);

                                            } catch (error) {
                                                console.error(
                                                    "Failed to save follow-up:",
                                                    error
                                                );

                                                toast.error(
                                                    "Failed to save follow-up date."
                                                );
                                            }
                                        }}
                                        className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl font-semibold transition"
                                    >
                                        Save
                                    </button>
                                </div>
                            </div>


                            {/* Deal Value */}
                            <div>
                                <label className="font-semibold block mb-2 text-gray-800">
                                    Deal Value
                                </label>

                                <div className="flex gap-2">

                                    <input
                                        type="number"
                                        min="0"
                                        step="0.01"
                                        value={
                                            lead.deal_value !== null &&
                                            lead.deal_value !== undefined
                                                ? lead.deal_value
                                                : ""
                                        }
                                        onChange={(e) =>
                                            setLead({
                                                ...lead,
                                                deal_value: e.target.value
                                            })
                                        }
                                        placeholder="Enter deal value"
                                        className="flex-1 border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                                    />

                                    <button
                                        onClick={async () => {
                                            try {
                                                const value = Number(lead.deal_value);

                                                if (
                                                    lead.deal_value === "" ||
                                                    lead.deal_value === null ||
                                                    lead.deal_value === undefined ||
                                                    !Number.isFinite(value) ||
                                                    value < 0
                                                ) {
                                                    toast.error(
                                                        "Please enter a valid deal value."
                                                    );
                                                    return;
                                                }

                                                const formData = new FormData();

                                                formData.append(
                                                    "deal_value",
                                                    String(value)
                                                );

                                                const response = await api.post(
                                                    `/lead/${lead.id}/deal-value`,
                                                    formData
                                                );

                                                if (!response.data?.success) {
                                                    throw new Error(
                                                        "Deal value was not saved"
                                                    );
                                                }

                                                toast.success(
                                                    "Deal value saved successfully!"
                                                );

                                                const refreshed = await api.get(
                                                    `/lead/${lead.id}`
                                                );

                                                setLead(refreshed.data);

                                            } catch (error) {
                                                console.error(
                                                    "Failed to save deal value:",
                                                    error
                                                );

                                                toast.error(
                                                    "Failed to save deal value."
                                                );
                                            }
                                        }}
                                        className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl font-semibold transition"
                                    >
                                        Save
                                    </button>

                                </div>
                            </div>

                        </div>

                    </div>

                </div>


                {/* =====================================================
                    CRM STATE
                ====================================================== */}

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">

                    {/* Proposal Sent */}
                    <div className="rounded-xl border border-gray-200 p-4 bg-white">

                        <div className="text-sm text-gray-500 mb-2">
                            Proposal Sent
                        </div>

                        <select
                            value={
                                lead.proposal_sent === true
                                    ? "Yes"
                                    : "No"
                            }
                            onChange={(e) =>
                                updateCRMState({
                                    proposal_sent:
                                        e.target.value === "Yes"
                                })
                            }
                            className="w-full border border-gray-300 rounded-xl px-3 py-2 bg-white text-gray-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        >
                            <option value="No">
                                No
                            </option>

                            <option value="Yes">
                                Yes
                            </option>
                        </select>

                    </div>


                    {/* Meeting Scheduled */}
                    <div className="rounded-xl border border-gray-200 p-4 bg-white">

                        <div className="text-sm text-gray-500 mb-2">
                            Meeting Scheduled
                        </div>

                        <select
                            value={
                                lead.meeting_scheduled === true
                                    ? "Yes"
                                    : "No"
                            }
                            onChange={(e) =>
                                updateCRMState({
                                    meeting_scheduled:
                                        e.target.value === "Yes"
                                })
                            }
                            className="w-full border border-gray-300 rounded-xl px-3 py-2 bg-white text-gray-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        >
                            <option value="No">
                                No
                            </option>

                            <option value="Yes">
                                Yes
                            </option>
                        </select>

                    </div>


                    {/* Outcome */}
                    <div className="rounded-xl border border-gray-200 p-4 bg-white">

                        <div className="text-sm text-gray-500 mb-2">
                            Outcome
                        </div>

                        <select
                            value={
                                lead.won === true
                                    ? "Won"
                                    : lead.lost === true
                                        ? "Lost"
                                        : "Open"
                            }
                            onChange={(e) =>
                                updateCRMState({
                                    outcome: e.target.value
                                })
                            }
                            className="w-full border border-gray-300 rounded-xl px-3 py-2 bg-white text-gray-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        >
                            <option value="Open">
                                Open
                            </option>

                            <option value="Won">
                                Won
                            </option>

                            <option value="Lost">
                                Lost
                            </option>
                        </select>

                    </div>

                </div>
            </section>


            {/* =====================================================
                OUTREACH
            ====================================================== */}

            <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">

                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">

                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">
                            ✉️ Outreach
                        </h2>

                        <p className="text-gray-500 mt-1">
                            Generate and review a personalized AI outreach message.
                        </p>
                    </div>

                    <button
                        onClick={generateOutreach}
                        disabled={generatingOutreach || isContactDisabled}
                        title={
                            isContactDisabled
                                ? `This opportunity is ${lead.opportunity_status} and outreach is disabled.`
                                : "Generate personalized AI outreach"
                        }
                        className={`px-5 py-3 rounded-xl font-semibold transition ${
                            isContactDisabled
                                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                                : "bg-blue-600 hover:bg-blue-700 text-white"
                        }`}
                    >
                        {isContactDisabled
                            ? `🚫 ${lead.opportunity_status}`
                            : generatingOutreach
                                ? "Generating..."
                                : outreachMessage
                                    ? "Regenerate Message"
                                    : "Generate AI Outreach"}
                    </button>

                </div>


                {/* Outreach Strategy */}

                <div className="bg-gray-50 rounded-2xl p-5 mb-5">

                    <h3 className="font-bold text-gray-800 mb-3">
                        Outreach Strategy
                    </h3>

                    <p className="text-gray-700 leading-7 whitespace-pre-line">
                        {lead.outreach_strategy ||
                            "No outreach strategy has been generated for this lead yet."}
                    </p>

                </div>


                {/* AI Outreach Message */}

                <div className="border border-blue-200 bg-blue-50 rounded-2xl p-5">

                    <div className="flex items-center justify-between gap-3 mb-4">

                        <h3 className="font-bold text-gray-800">
                            AI Outreach Message
                        </h3>

                        {outreachMessage && (
                            <div className="flex gap-2">

                                <button
                                    onClick={saveOutreach}
                                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold transition"
                                >
                                    Save Outreach
                                </button>

                                <button
                                    onClick={async () => {
                                        try {
                                            await navigator.clipboard.writeText(
                                                `${outreachSubject}\n\n${outreachMessage}`
                                            );

                                            toast.success(
                                                "Outreach message copied!"
                                            );

                                        } catch (error) {
                                            console.error(
                                                "Failed to copy message:",
                                                error
                                            );

                                            toast.error(
                                                "Failed to copy message."
                                            );
                                        }
                                    }}
                                    className="bg-gray-800 hover:bg-gray-900 text-white px-4 py-2 rounded-lg font-semibold transition"
                                >
                                    Copy Message
                                </button>

                            </div>
                        )}


                    </div>


                    {outreachMessage ? (
                        <div className="space-y-4">

                            <div>
                                <label className="block text-sm font-semibold text-gray-600 mb-2">
                                    Subject
                                </label>

                                <input
                                    type="text"
                                    value={outreachSubject}
                                    onChange={(e) =>
                                        setOutreachSubject(e.target.value)
                                    }
                                    className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                                />
                            </div>


                            <div>
                                <label className="block text-sm font-semibold text-gray-600 mb-2">
                                    Message
                                </label>

                                <textarea
                                    value={outreachMessage}
                                    onChange={(e) =>
                                        setOutreachMessage(e.target.value)
                                    }
                                    rows={8}
                                    className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none resize-y"
                                />
                            </div>

                        </div>
                    ) : (
                        <div className="text-gray-500 py-4">
                            No AI outreach message generated yet.
                            Click <strong>Generate AI Outreach</strong> to create one.
                        </div>
                    )}

                </div>

                {isContactDisabled && (
                    <div className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-700">
                        <strong>Contact disabled:</strong>{" "}
                        This opportunity is marked as{" "}
                        <strong>{lead.opportunity_status}</strong>.
                        It should not be contacted.
                    </div>
                )}

                {/* Contact Actions */}

                <div className="flex flex-wrap gap-3 mt-5">

                    <button
                        onClick={markAsContacted}
                        disabled={isContactDisabled}
                        title={
                            isContactDisabled
                                ? `This opportunity is ${lead.opportunity_status} and cannot be contacted.`
                                : "Mark this lead as contacted"
                        }
                        className={`inline-flex items-center gap-2 px-5 py-3 rounded-xl font-semibold transition ${
                            isContactDisabled
                                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                                : "bg-green-600 hover:bg-green-700 text-white"
                        }`}
                    >
                        {isContactDisabled
                            ? `🚫 ${lead.opportunity_status}`
                            : "✓ Mark as Contacted"}
                    </button>

                    {lead.email && (
                        <button
                            onClick={contactViaEmail}
                            disabled={isContactDisabled}
                            title={
                                isContactDisabled
                                    ? `This opportunity is ${lead.opportunity_status} and cannot be contacted.`
                                    : "Contact this lead via email"
                            }
                            className={`inline-flex items-center gap-2 px-5 py-3 rounded-xl font-semibold transition ${
                                isContactDisabled
                                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                                    : "bg-blue-600 hover:bg-blue-700 text-white"
                            }`}
                        >
                            {isContactDisabled
                                ? "🚫 Contact Disabled"
                                : "✉️ Contact via Email"}
                        </button>
                    )}

                    {lead.website && (
                        <a
                            href={lead.website}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-2 bg-gray-800 hover:bg-gray-900 text-white px-5 py-3 rounded-xl font-semibold transition"
                        >
                            🌐 Visit Website
                        </a>
                    )}

                    {lead.linkedin && (
                        <a
                            href={lead.linkedin}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-3 rounded-xl font-semibold transition"
                        >
                            💼 LinkedIn
                        </a>
                    )}

                </div>

            </section>


            {/* =====================================================
                DESCRIPTION
            ====================================================== */}

            <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">

                <h2 className="text-xl font-bold text-gray-900 mb-4">
                    📝 Lead Description
                </h2>

                <div className="bg-gray-50 rounded-2xl p-5">

                    <p className="text-gray-700 leading-8 whitespace-pre-line">
                        {lead.description || "No description available."}
                    </p>

                </div>

            </section>


            {/* =====================================================
                SOURCE + METADATA
            ====================================================== */}

            <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">

                <h2 className="text-xl font-bold text-gray-900 mb-4">
                    🔗 Source & Metadata
                </h2>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    <div className="bg-gray-50 rounded-2xl p-5 space-y-4">

                        <InfoRow
                            label="Source Type"
                            value={lead.source_type}
                        />

                        <InfoRow
                            label="Source Confidence"
                            value={
                                lead.source_confidence !== null &&
                                lead.source_confidence !== undefined
                                    ? `${lead.source_confidence}%`
                                    : "—"
                            }
                        />

                        {/* Opportunity Status */}
                        <InfoRow label="Opportunity Status">
                            <span
                                className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                                    lead.opportunity_status === "OPEN"
                                        ? "bg-green-100 text-green-700"
                                        : lead.opportunity_status === "CLOSED"
                                        ? "bg-red-100 text-red-700"
                                        : lead.opportunity_status === "EXPIRED"
                                        ? "bg-orange-100 text-orange-700"
                                        : lead.opportunity_status === "REMOVED"
                                        ? "bg-gray-200 text-gray-700"
                                        : "bg-gray-100 text-gray-700"
                                }`}
                            >
                                {lead.opportunity_status || "UNKNOWN"}
                            </span>
                        </InfoRow>

                        {/* Source Status */}
                        <InfoRow
                            label="Source Status"
                            value={lead.source_status}
                        />

                        {/* Freshness Check */}
                        <InfoRow
                            label="Last Freshness Check"
                            value={formatDate(lead.freshness_checked_at)}
                        />

                        <InfoRow
                            label="Submitted"
                            value={formatDate(lead.submitted_at)}
                        />

                        <InfoRow
                            label="Updated"
                            value={formatDate(lead.updated_at)}
                        />

                    </div>

                    <div className="bg-gray-50 rounded-2xl p-5">

                        <p className="text-gray-500 mb-4">
                            View the original post or business requirement.
                        </p>

                        {lead.link ? (
                            <a
                                href={lead.link}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold transition shadow-sm"
                            >
                                🌐 Open Original Post ↗
                            </a>
                        ) : (
                            <span className="text-gray-500">
                                Original source link unavailable.
                            </span>
                        )}

                    </div>

                </div>

            </section>


            {/* =====================================================
                FOOTER ACTION
            ====================================================== */}

            <div className="flex justify-start">

                <button
                    onClick={() => navigate("/leads")}
                    className="px-6 py-3 rounded-xl border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 font-semibold transition"
                >
                    ← Back to All Leads
                </button>

            </div>

        </div>
    );
}

export default LeadDetails;