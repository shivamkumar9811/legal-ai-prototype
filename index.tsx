import React from "react";
import { createRoot } from "react-dom/client";
import App from "./components/App";

import addOnUISdk from "https://new.express.adobe.com/static/add-on-sdk/sdk.js";

(window as any).addOnUISdk = addOnUISdk;


addOnUISdk.ready.then(() => {
    console.log("addOnUISdk is ready for use.");

    const root = createRoot(document.getElementById("root"));
    root.render(<App />);
});

