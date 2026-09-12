import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

function DashboardLayout({ children }) {

    return (

        <div className="flex min-h-screen bg-gray-100">

            <Sidebar />

            <div className="flex-1 flex flex-col">

                <Navbar />

                <main className="flex-1 overflow-auto p-8">

                    {children}

                </main>

            </div>

        </div>

    );

}

export default DashboardLayout;