import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [extractedText, setExtractedText] = useState("");

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setExtractedText(response.data.text);
        } catch (error) {
            console.error("Error:", error);
            setExtractedText("Failed to extract text. Please try again.");
        }
    };

    return (
        <div className="container">
            <h1 className="title">📄 OCR Text Extractor 🖋️</h1>
            <div className="upload-section">
                <input type="file" onChange={handleFileChange} className="file-input" />
                <button onClick={handleUpload} className="upload-button">🚀 Extract Text</button>
            </div>
            <div className="output-box">
                <h2>📝 Extracted Text:</h2>
                <pre>{extractedText || "Upload an image to extract text."}</pre>
            </div>
        </div>
    );
}

export default App;
