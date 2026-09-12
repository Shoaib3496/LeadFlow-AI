import { useEffect, useState } from "react";
import api from "../services/api";

function Settings() {

    const [settings, setSettings] = useState({
        hotLead: true,
        pipelineCompleted: true,
        pipelineFailed: true
    });

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState("");
    const [message, setMessage] = useState("");

    useEffect(() => {
        loadSettings();
    }, []);

    async function loadSettings() {

        try {

            setLoading(true);

            const response = await api.get("/notification-settings");

            setSettings(response.data);

        } catch (error) {

            console.error("Failed to load notification settings:", error);

            setMessage("Failed to load notification settings.");

        } finally {

            setLoading(false);

        }

    }

    async function toggleSetting(key) {

        const updatedSettings = {
            ...settings,
            [key]: !settings[key]
        };

        try {

            setSaving(key);
            setMessage("");

            const response = await api.put(
                "/notification-settings",
                updatedSettings
            );

            setSettings(response.data.settings);

            setMessage("Settings saved successfully.");

        } catch (error) {

            console.error(
                "Failed to update notification settings:",
                error
            );

            setMessage("Failed to save settings.");

        } finally {

            setSaving("");

        }

    }

    async function resetSettings() {

        const defaultSettings = {
            hotLead: true,
            pipelineCompleted: true,
            pipelineFailed: true
        };

        try {

            setSaving("reset");
            setMessage("");

            const response = await api.put(
                "/notification-settings",
                defaultSettings
            );

            setSettings(response.data.settings);

            setMessage("Notification settings reset.");

        } catch (error) {

            console.error(
                "Failed to reset notification settings:",
                error
            );

            setMessage("Failed to reset settings.");

        } finally {

            setSaving("");

        }

    }

    const notificationOptions = [
        {
            key: "hotLead",
            title: "HOT Lead Notifications",
            description:
                "Notify when a lead receives HOT commercial priority.",
            icon: "🔥"
        },
        {
            key: "pipelineCompleted",
            title: "Pipeline Completion",
            description:
                "Notify when the production lead pipeline finishes successfully.",
            icon: "✓"
        },
        {
            key: "pipelineFailed",
            title: "Pipeline Failure",
            description:
                "Notify when the production lead pipeline fails.",
            icon: "!"
        }
    ];

    if (loading) {

        return (

            <div className="max-w-4xl mx-auto">

                <h1 className="text-3xl font-bold text-gray-900 mb-8">
                    Settings
                </h1>

                <div className="bg-white rounded-2xl shadow border border-gray-100 p-8">

                    <p className="text-gray-500">
                        Loading settings...
                    </p>

                </div>

            </div>

        );

    }

    return (

        <div className="max-w-4xl mx-auto space-y-8">

            <div>

                <h1 className="text-3xl font-bold text-gray-900">
                    Settings
                </h1>

                <p className="text-gray-500 mt-2">
                    Manage LeadFlow AI notification preferences.
                </p>

            </div>

            {message && (

                <div className="bg-blue-50 border border-blue-200 text-blue-700 rounded-xl px-5 py-3">
                    {message}
                </div>

            )}

            <div className="bg-white rounded-2xl shadow border border-gray-100 overflow-hidden">

                <div className="px-6 py-5 border-b border-gray-100">

                    <h2 className="text-xl font-bold text-gray-900">
                        Notifications
                    </h2>

                    <p className="text-sm text-gray-500 mt-1">
                        Control which pipeline events generate notifications.
                    </p>

                </div>

                <div>

                    {notificationOptions.map((option, index) => (

                        <div
                            key={option.key}
                            className={`
                                px-6 py-5
                                flex items-center justify-between gap-6
                                ${index !== notificationOptions.length - 1
                                    ? "border-b border-gray-100"
                                    : ""}
                            `}
                        >

                            <div className="flex items-start gap-4">

                                <div className="text-2xl">
                                    {option.icon}
                                </div>

                                <div>

                                    <h3 className="font-semibold text-gray-900">
                                        {option.title}
                                    </h3>

                                    <p className="text-sm text-gray-500 mt-1">
                                        {option.description}
                                    </p>

                                </div>

                            </div>

                            <button
                                type="button"
                                onClick={() => toggleSetting(option.key)}
                                disabled={saving === option.key}
                                className={`
                                    relative
                                    inline-flex
                                    h-7
                                    w-12
                                    flex-shrink-0
                                    items-center
                                    rounded-full
                                    transition-colors
                                    duration-200
                                    disabled:opacity-50
                                    ${
                                        settings[option.key]
                                            ? "bg-blue-600"
                                            : "bg-gray-300"
                                    }
                                `}
                                aria-label={`Toggle ${option.title}`}
                            >

                                <span
                                    className={`
                                        inline-block
                                        h-5
                                        w-5
                                        transform
                                        rounded-full
                                        bg-white
                                        shadow
                                        transition-transform
                                        duration-200
                                        ${
                                            settings[option.key]
                                                ? "translate-x-6"
                                                : "translate-x-1"
                                        }
                                    `}
                                />

                            </button>

                        </div>

                    ))}

                </div>

            </div>

            <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">

                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">

                    <div>

                        <h2 className="font-semibold text-gray-900">
                            Reset Notifications
                        </h2>

                        <p className="text-sm text-gray-500 mt-1">
                            Enable all notification types.
                        </p>

                    </div>

                    <button
                        type="button"
                        onClick={resetSettings}
                        disabled={saving === "reset"}
                        className="
                            bg-gray-100
                            hover:bg-gray-200
                            text-gray-800
                            px-5
                            py-2.5
                            rounded-lg
                            font-medium
                            transition
                            disabled:opacity-50
                        "
                    >

                        {saving === "reset"
                            ? "Resetting..."
                            : "Reset to Defaults"}

                    </button>

                </div>

            </div>

        </div>

    );

}

export default Settings;
