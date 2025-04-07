import { Link } from 'react-router-dom';

function Home() {
  const isLoggedIn = !!localStorage.getItem('token');

  return (
    <div className="max-w-4xl mx-auto text-center">
      <h1 className="text-4xl font-bold mb-6 pt-1 bg-gradient-to-r from-cyan-500 to-red-400 bg-clip-text text-transparent ">Welcome to OCR App</h1>
      
      <p className="text-xl mb-8 text-gray-300">
        Upload images and extract text using our powerful OCR technology.
      </p>
      
      <div className="flex justify-center space-x-4">
        {isLoggedIn ? (
          <Link
            to="/dashboard"
            className="bg-cyan-500 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-lg"
          >
            Go to Dashboard
          </Link>
        ) : (
          <>
            <Link
              to="/login"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-6 rounded-lg"
            >
              Register
            </Link>
          </>
        )}
      </div>
      
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-cyan-800 p-6 rounded-lg shadow-md border border-white">
          <h2 className="text-xl font-bold mb-4 text-white-400 ">Easy Registration</h2>
          <p>Create an account in seconds to get started with our OCR service.</p>
        </div>
        
        <div className="bg-cyan-800 p-6 rounded-lg shadow-md border border-white">
          <h2 className="text-xl font-bold mb-4 text-white-400">Simple Upload</h2>
          <p>Upload your images with a simple drag and drop or file selection.</p>
        </div>
        
        <div className="bg-cyan-800 p-6 rounded-lg shadow-md border border-white">
          <h2 className="text-xl font-bold mb-4">Powerful OCR</h2>
          <p>Extract text from images using our advanced OCR technology.</p>
        </div>
      </div>
    </div>
  );
}

export default Home;