function Badge({
    children,
    color = "gray",
}) {

    const colors = {

        green: "bg-green-100 text-green-700",

        red: "bg-red-100 text-red-700",

        blue: "bg-blue-100 text-blue-700",

        yellow: "bg-yellow-100 text-yellow-700",

        purple: "bg-purple-100 text-purple-700",

        gray: "bg-gray-100 text-gray-700",

        indigo: "bg-indigo-100 text-indigo-700",

    };

    return (

        <span
            className={`
                inline-flex
                items-center
                px-3
                py-1
                rounded-full
                text-sm
                font-semibold
                ${colors[color]}
            `}
        >

            {children}

        </span>

    );

}

export default Badge;