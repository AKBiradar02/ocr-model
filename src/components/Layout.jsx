import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

function Layout() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="text-white p-4 bg-gradient-to-r from-cyan-800 to-red-400 ">
        <div className="container mx-auto flex justify-between items-center">
          <Link to="/" className="text-xl font-bold bg-gradient-to-r from-cyan-800 ">OCR App</Link>
          <nav className="space-x-4">
            {isLoggedIn ? (
              <>
                <Link to="/dashboard" className="hover:underline">Dashboard</Link>
                <button onClick={handleLogout} className="hover:underline">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:underline text-lg">Login</Link>
                <Link to="/register" className="hover:underline text-lg">Register</Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="flex-grow container mx-auto p-4">
        <Outlet />
      </main>
      <footer className="bg-gradient-to-r from-cyan-800 to-red-400 p-5 mb-15">
        <div className="container mx-auto text-center text-black ">
          <p>© {new Date().getFullYear()} OCR App. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default Layout;