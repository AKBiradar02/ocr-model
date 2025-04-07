import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [ocrText, setOcrText] = useState('');
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    const userData = JSON.parse(localStorage.getItem('currentUser') || '{}');
    setUser(userData);
  }, [navigate]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      
      // Create a preview URL
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
      
      // Reset OCR text when a new file is selected
      setOcrText('');
    }
  };

  const handleOCR = async () => {
    if (!file) return;
    
    setIsProcessing(true);
    
    try {
      // Create form data for file upload
      const formData = new FormData();
      formData.append('file', file);
      
      // Get token from localStorage
      const token = localStorage.getItem('token');
      
      // Send request to Flask backend
      const response = await fetch('http://localhost:5000/api/ocr', {
        method: 'POST',
        headers: {
          'x-access-token': token
        },
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Error processing file');
      }
      
      const data = await response.json();
      setOcrText(data.text);
    } catch (error) {
      console.error('OCR Error:', error);
      alert('Error processing the image: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    navigate('/login');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button 
          onClick={handleLogout}
          className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
        >
          Logout
        </button>
      </div>
      
      {user && (
        <div className="p-4 rounded mb-6">
          <p className="font-medium text-2xl">Welcome, {user.name}!</p>
        </div>
      )}
      
      <div className="bg-gradient-to-r from-cyan-800 to-red-300 shadow-md rounded p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4 text-lg-black-500">Upload Image for OCR</h2>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="file">
            Select an image file (JPG, PNG, etc.)
          </label>
          <input
            type="file"
            id="file"
            accept="image/*"
            onChange={handleFileChange}
            className="w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
        </div>
        
        {preview && (
          <div className="mb-4">
            <h3 className="text-lg font-medium mb-2">Preview:</h3>
            <img 
              src={preview} 
              alt="Preview" 
              className="max-w-full h-auto max-h-96 border rounded"
            />
          </div>
        )}
        
        <button
          onClick={handleOCR}
          disabled={!file || isProcessing}
          className={`w-full py-2 px-4 rounded font-bold ${
            !file || isProcessing
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-700 text-white'
          }`}
        >
          {isProcessing ? 'Processing...' : 'Extract Text (OCR)'}
        </button>
      </div>
      
      {isProcessing && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded mb-6">
          <p className="font-medium">Processing your image... This may take a moment.</p>
        </div>
      )}
      
      {ocrText && (
        <div className="bg-gradient-to-r from-cyan-800 to-red-300 shadow-md rounded p-6">
          <h2 className="text-xl font-semibold mb-4">Extracted Text</h2>
          <div className="bg-gray-50 p-4 rounded border whitespace-pre-wrap font-mono text-black">
            {ocrText}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;