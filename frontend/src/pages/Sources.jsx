import { useEffect, useState } from "react";
import api from "../services/api";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";
import LoadingSpinner from "../components/ui/LoadingSpinner";

function Sources() {

    const [sources, setSources] = useState([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(false);

    const [showAddForm, setShowAddForm] = useState(false);

    const [selectedSource, setSelectedSource] = useState(null);
    const [showViewModal, setShowViewModal] = useState(false);

    const [newSource, setNewSource] = useState({
        name: "",
        category: "",
        country: "",
        enabled: true
    });

    const [addingSource, setAddingSource] = useState(false);
    const [addError, setAddError] = useState("");

    async function loadSources() {

        try {

            setLoading(true);

            const response = await api.get("/sources");

            setSources(response.data);

        } catch (error) {

            console.error(error);

        } finally {

            setLoading(false);

        }

    }

    useEffect(() => {

        loadSources();

    }, []);

    async function toggleSource(source) {

        try {

            await api.put(`/sources/${source.id}`, {

                enabled: !source.enabled

            });

            loadSources();

        } catch (error) {

            console.error(error);

        }

    }

    function viewSource(source) {

        setSelectedSource(source);
        setShowViewModal(true);

    }

    async function addSource(e) {

        e.preventDefault();

        setAddError("");

        if (!newSource.name.trim()) {
            setAddError("Source name is required.");
            return;
        }

        if (!newSource.category.trim()) {
            setAddError("Source category is required.");
            return;
        }

        if (!newSource.country.trim()) {
            setAddError("Source country is required.");
            return;
        }

        try {

            setAddingSource(true);

            await api.post("/sources", {
                name: newSource.name.trim(),
                category: newSource.category.trim(),
                country: newSource.country.trim(),
                enabled: newSource.enabled
            });

            setNewSource({
                name: "",
                category: "",
                country: "",
                enabled: true
            });

            setShowAddForm(false);

            await loadSources();

        } catch (error) {

            console.error("Add Source Error:", error);

            setAddError(
                error.response?.data?.detail ||
                "Failed to add source."
            );

        } finally {

            setAddingSource(false);

        }

    }

    const filteredSources = sources.filter((source) =>

        (source.name || "")
            .toLowerCase()
            .includes(search.toLowerCase()) ||

        (source.category || "")
            .toLowerCase()
            .includes(search.toLowerCase()) ||

        (source.country || "")
            .toLowerCase()
            .includes(search.toLowerCase())

    );

    return (

        <div className="max-w-7xl mx-auto space-y-8">

            <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">

                <div>

                    <h1 className="text-4xl font-bold text-gray-900">

                        Lead Sources

                    </h1>

                    <p className="text-gray-500 mt-2">

                        Manage all lead sources used by the AI pipeline.

                    </p>

                </div>

                <Button
                    variant="primary"
                    onClick={() => {
                        setShowAddForm(true);
                        setAddError("");
                    }}
                >
                    + Add Source
                </Button>

            </div>

            {showAddForm && (

                <Card className="p-6">

                    <div className="flex justify-between items-center mb-6">

                        <div>

                            <h2 className="text-xl font-bold text-gray-900">
                                Add Source
                            </h2>

                            <p className="text-gray-500 mt-1">
                                Add a new lead source to the system.
                            </p>

                        </div>

                        <Button
                            variant="secondary"
                            onClick={() => {
                                setShowAddForm(false);
                                setAddError("");
                            }}
                        >
                            Cancel
                        </Button>

                    </div>

                    <form
                        onSubmit={addSource}
                        className="grid grid-cols-1 md:grid-cols-3 gap-6"
                    >

                        <div>

                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Source Name
                            </label>

                            <input
                                type="text"
                                value={newSource.name}
                                onChange={(e) =>
                                    setNewSource({
                                        ...newSource,
                                        name: e.target.value
                                    })
                                }
                                placeholder="e.g. LinkedIn"
                                className="
                                    w-full
                                    border
                                    border-gray-300
                                    rounded-xl
                                    px-4
                                    py-3
                                    focus:ring-2
                                    focus:ring-blue-500
                                    outline-none
                                "
                            />

                        </div>

                        <div>

                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Category
                            </label>

                            <input
                                type="text"
                                value={newSource.category}
                                onChange={(e) =>
                                    setNewSource({
                                        ...newSource,
                                        category: e.target.value
                                    })
                                }
                                placeholder="e.g. Social"
                                className="
                                    w-full
                                    border
                                    border-gray-300
                                    rounded-xl
                                    px-4
                                    py-3
                                    focus:ring-2
                                    focus:ring-blue-500
                                    outline-none
                                "
                            />

                        </div>

                        <div>

                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Country
                            </label>

                            <input
                                type="text"
                                value={newSource.country}
                                onChange={(e) =>
                                    setNewSource({
                                        ...newSource,
                                        country: e.target.value
                                    })
                                }
                                placeholder="e.g. Global"
                                className="
                                    w-full
                                    border
                                    border-gray-300
                                    rounded-xl
                                    px-4
                                    py-3
                                    focus:ring-2
                                    focus:ring-blue-500
                                    outline-none
                                "
                            />

                        </div>

                        <div className="md:col-span-3 flex items-center justify-between">

                            <label className="flex items-center gap-3 text-sm text-gray-700">

                                <input
                                    type="checkbox"
                                    checked={newSource.enabled}
                                    onChange={(e) =>
                                        setNewSource({
                                            ...newSource,
                                            enabled: e.target.checked
                                        })
                                    }
                                    className="w-4 h-4"
                                />

                                Enable source immediately

                            </label>

                            <Button
                                variant="primary"
                                type="submit"
                                disabled={addingSource}
                            >
                                {addingSource
                                    ? "Adding..."
                                    : "Add Source"}
                            </Button>

                        </div>

                        {addError && (

                            <div className="md:col-span-3">

                                <p className="text-red-600 text-sm font-medium">
                                    {addError}
                                </p>

                            </div>

                        )}

                    </form>

                </Card>

            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                <Card className="p-6">

                    <p className="text-gray-500">Total Sources</p>

                    <h2 className="text-3xl font-bold mt-2">

                        {sources.length}

                    </h2>

                </Card>

                <Card className="p-6">

                    <p className="text-green-600">Enabled</p>

                    <h2 className="text-3xl font-bold mt-2">

                        {sources.filter(s => s.enabled).length}

                    </h2>

                </Card>

                <Card className="p-6">

                    <p className="text-red-600">Disabled</p>

                    <h2 className="text-3xl font-bold mt-2">

                        {sources.filter(s => !s.enabled).length}

                    </h2>

                </Card>

            </div>

            <div className="flex flex-col md:flex-row justify-between gap-4">

                <input
                    type="text"
                    placeholder="Search source..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="
                        w-full
                        md:w-96
                        border
                        border-gray-300
                        rounded-xl
                        px-4
                        py-3
                        focus:ring-2
                        focus:ring-blue-500
                        outline-none
                    "
                />

                <Button
                    variant="secondary"
                    onClick={loadSources}
                    disabled={loading}
                >
                    {loading ? "Refreshing..." : "🔄 Refresh"}
                </Button>

            </div>

            {loading ? (

                <Card>

                    <LoadingSpinner text="Loading sources..." />

                </Card>

            ) : (

                <Card className="overflow-hidden">

                    <table className="w-full">

                        <thead className="bg-gray-50 border-b">

                            <tr>

                                <th className="px-6 py-4 text-left text-sm font-bold uppercase tracking-wide text-gray-600">
                                    Name
                                </th>

                                <th className="px-6 py-4 text-left text-sm font-bold uppercase tracking-wide text-gray-600">
                                    Category
                                </th>

                                <th className="px-6 py-4 text-left text-sm font-bold uppercase tracking-wide text-gray-600">
                                    Country
                                </th>

                                <th className="px-6 py-4 text-left text-sm font-bold uppercase tracking-wide text-gray-600">
                                    Status
                                </th>

                                <th className="px-6 py-4 text-left text-sm font-bold uppercase tracking-wide text-gray-600">
                                    Action
                                </th>

                            </tr>

                        </thead>

                        <tbody>

                            {filteredSources.length === 0 ? (

                                <tr>

                                    <td
                                        colSpan="5"
                                        className="px-6 py-10 text-center text-gray-500 font-medium"
                                    >

                                        No sources found.

                                    </td>

                                </tr>

                            ) : (

                                filteredSources.map((source) => (

                                    <tr
                                        key={source.id}
                                        className="
                                            border-b
                                            last:border-none
                                            hover:bg-blue-50
                                            transition-colors
                                        "
                                    >

                                        <td className="px-6 py-5">

                                            <div className="flex items-center gap-3">

                                                <span className="text-2xl">

                                                    {source.name === "Reddit"
                                                        ? "👽"
                                                        : source.name === "Hacker News"
                                                        ? "💻"
                                                        : source.name === "RSS"
                                                        ? "📰"
                                                        : "🌐"}

                                                </span>

                                                <span className="font-semibold text-gray-800">

                                                    {source.name}

                                                </span>

                                            </div>

                                        </td>

                                        <td className="px-6 py-5">

                                            <Badge color="indigo">

                                                {source.category}

                                            </Badge>

                                        </td>

                                        <td className="px-6 py-5">

                                            <Badge>

                                                🌍 {source.country || "Global"}

                                            </Badge>

                                        </td>

                                        <td className="px-6 py-5">

                                            <Badge color={source.enabled ? "green" : "red"}>

                                                {source.enabled ? "🟢 Enabled" : "🔴 Disabled"}

                                            </Badge>

                                        </td>

                                        <td className="px-6 py-5">

                                            <div className="flex items-center gap-2">

                                                <Button
                                                    variant="secondary"
                                                    onClick={() => viewSource(source)}
                                                >
                                                    View
                                                </Button>

                                                <Button
                                                    variant={source.enabled ? "danger" : "success"}
                                                    onClick={() => toggleSource(source)}
                                                >
                                                    {source.enabled ? "Disable" : "Enable"}
                                                </Button>

                                            </div>

                                        </td>

                                    </tr>

                                ))

                            )}

                        </tbody>

                    </table>

                </Card>

            )}

            {showViewModal && selectedSource && (

                <div className="
                    fixed
                    inset-0
                    bg-black
                    bg-opacity-40
                    flex
                    items-center
                    justify-center
                    z-50
                    p-4
                ">

                    <div className="
                        bg-white
                        rounded-2xl
                        shadow-2xl
                        w-full
                        max-w-lg
                        p-6
                    ">

                        <div className="flex justify-between items-start mb-6">

                            <div>

                                <h2 className="text-2xl font-bold text-gray-900">
                                    Source Details
                                </h2>

                                <p className="text-gray-500 mt-1">
                                    View source information
                                </p>

                            </div>

                            <button
                                type="button"
                                onClick={() => {
                                    setShowViewModal(false);
                                    setSelectedSource(null);
                                }}
                                className="
                                    text-gray-500
                                    hover:text-gray-900
                                    text-2xl
                                    font-bold
                                "
                            >
                                ×
                            </button>

                        </div>

                        <div className="space-y-4">

                            <div className="flex justify-between border-b pb-3">

                                <span className="text-gray-500">
                                    Name
                                </span>

                                <span className="font-semibold text-gray-900">
                                    {selectedSource.name}
                                </span>

                            </div>

                            <div className="flex justify-between border-b pb-3">

                                <span className="text-gray-500">
                                    Category
                                </span>

                                <span className="font-semibold text-gray-900">
                                    {selectedSource.category}
                                </span>

                            </div>

                            <div className="flex justify-between border-b pb-3">

                                <span className="text-gray-500">
                                    Country
                                </span>

                                <span className="font-semibold text-gray-900">
                                    {selectedSource.country || "Global"}
                                </span>

                            </div>

                            <div className="flex justify-between border-b pb-3">

                                <span className="text-gray-500">
                                    Status
                                </span>

                                <Badge
                                    color={
                                        selectedSource.enabled
                                            ? "green"
                                            : "red"
                                    }
                                >
                                    {selectedSource.enabled
                                        ? "🟢 Enabled"
                                        : "🔴 Disabled"}
                                </Badge>

                            </div>

                            <div className="flex justify-between border-b pb-3">

                                <span className="text-gray-500">
                                    Last Run
                                </span>

                                <span className="font-medium text-gray-900">
                                    {selectedSource.last_run
                                        ? new Date(
                                            selectedSource.last_run
                                        ).toLocaleString()
                                        : "Never"}
                                </span>

                            </div>

                            <div className="flex justify-between border-b pb-3">

                                <span className="text-gray-500">
                                    Leads Collected
                                </span>

                                <span className="font-semibold text-gray-900">
                                    {selectedSource.leads_collected ?? 0}
                                </span>

                            </div>

                        </div>

                        <div className="flex justify-end mt-6">

                            <Button
                                variant="secondary"
                                onClick={() => {
                                    setShowViewModal(false);
                                    setSelectedSource(null);
                                }}
                            >
                                Close
                            </Button>

                        </div>

                    </div>

                </div>

            )}

        </div>

    );

}

export default Sources;