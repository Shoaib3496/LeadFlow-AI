function Button({
    children,
    onClick,
    type = "button",
    variant = "primary",
    disabled = false,
    className = "",
}) {

    const variants = {

        primary:
            "bg-blue-600 hover:bg-blue-700 text-white",

        success:
            "bg-green-600 hover:bg-green-700 text-white",

        danger:
            "bg-red-600 hover:bg-red-700 text-white",

        secondary:
            "bg-gray-700 hover:bg-gray-800 text-white",

    };

    return (

        <button
            type={type}
            onClick={onClick}
            disabled={disabled}
            className={`
                px-5
                py-2.5
                rounded-xl
                font-medium
                transition-all
                shadow
                hover:shadow-lg
                disabled:bg-gray-400
                disabled:cursor-not-allowed
                ${variants[variant]}
                ${className}
            `}
        >

            {children}

        </button>

    );

}

export default Button;