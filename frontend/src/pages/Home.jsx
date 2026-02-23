import { useState } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../api/client";

export default function Home() {
  const [showAuth, setShowAuth] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ name: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const deriveNameFromEmail = (email) =>
    (email || "").split("@")[0]?.replace(/[._-]+/g, " ").trim() || "New User";

  const handleAuth = async () => {
    setLoading(true);
    const endpoint = isLogin ? "/auth/login" : "/auth/register";
    try {
      const res = await apiClient.post(endpoint, {
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (res.ok) {
        if (data && data.user_id) {
          const authToken = data.token || data.access_token || "";
          localStorage.setItem("user_id", data.user_id);
          localStorage.setItem("user_name", data.name);
          if (authToken) {
            localStorage.setItem("token", authToken);
            localStorage.setItem("access_token", authToken);
          }
        }
        setShowAuth(false);
        navigate("/intake");
      } else {
        if (isLogin && res.status === 404) {
          setIsLogin(false);
          setFormData(prev => ({
            ...prev,
            name: prev.name || deriveNameFromEmail(prev.email),
          }));
          alert("No account found for this email. Switched to Register mode.");
          setLoading(false);
          return;
        }
        alert(data.detail || "Something went wrong");
      }
    } catch (err) {
      alert("Cannot connect to server. Start backend with: `cd backend && uvicorn app.main:app --reload --port 8000` (or `uvicorn main:app --reload --port 8000`).");
    }
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-white flex flex-col">
      <div className="border-b border-zinc-800 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="text-zinc-400 text-xs uppercase tracking-widest font-medium">Physique Modeling System</span>
        </div>
        <span className="text-zinc-600 text-xs">Experimental Model v0.3</span>
      </div>

      <div className="flex flex-col items-start justify-center flex-1 max-w-3xl mx-auto w-full px-8 py-20">
        <p className="text-emerald-500 text-xs uppercase tracking-widest font-medium mb-6">Anthropometric Analysis</p>
        <h1 className="text-5xl font-semibold text-zinc-100 leading-tight mb-4 tracking-tight">
          Coachify <br />
        </h1>
        <p className="text-zinc-400 text-lg leading-relaxed mb-12 max-w-xl">
          Structural analysis and projected adaptation modeling based on anthropometric inputs, FFMI estimation, and Muscle Growth research data.
        </p>

        <div className="grid grid-cols-3 gap-px bg-zinc-800 border border-zinc-800 rounded-xl overflow-hidden mb-12 w-full max-w-lg">
          {[
            { label: "Analysis Method", value: "CV + ML" },
            { label: "Data Points", value: "14 inputs" },
            { label: "Confidence Range", value: "±8%" },
          ].map(item => (
            <div key={item.label} className="bg-zinc-900 px-5 py-4">
              <p className="text-zinc-500 text-xs uppercase tracking-wider mb-1">{item.label}</p>
              <p className="text-zinc-100 text-sm font-medium">{item.value}</p>
            </div>
          ))}
        </div>

        <p className="text-zinc-600 text-xs leading-relaxed mb-10 max-w-lg border-l border-zinc-700 pl-4">
          Estimates are based on structural frame modeling, lean mass index projections, and historical hypertrophy adaptation data. Results represent probabilistic ranges, not guarantees.
        </p>

        <button
          onClick={() => setShowAuth(true)}
          className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors duration-150"
        >
          Begin Analysis
        </button>
      </div>

      {showAuth && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 px-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 w-full max-w-sm relative">
            <button onClick={() => setShowAuth(false)}
              className="absolute top-4 right-4 text-zinc-600 hover:text-zinc-300 text-sm transition-colors">✕</button>

            <p className="text-zinc-500 text-xs uppercase tracking-widest mb-6">
              {isLogin ? "Returning User" : "New User"}
            </p>

            <div className="flex bg-zinc-800 border border-zinc-700 rounded-lg p-1 mb-6">
              <button onClick={() => setIsLogin(true)}
                className={`flex-1 py-2 rounded-md text-xs font-medium uppercase tracking-wide transition-all ${isLogin ? "bg-emerald-600 text-white" : "text-zinc-500 hover:text-zinc-300"}`}>
                Sign In
              </button>
              <button onClick={() => setIsLogin(false)}
                className={`flex-1 py-2 rounded-md text-xs font-medium uppercase tracking-wide transition-all ${!isLogin ? "bg-emerald-600 text-white" : "text-zinc-500 hover:text-zinc-300"}`}>
                Register
              </button>
            </div>

            <div className="space-y-4">
              {!isLogin && (
                <div>
                  <label className="text-zinc-500 text-xs uppercase tracking-wider mb-1.5 block">Full Name</label>
                  <input type="text" placeholder="John Smith" value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-emerald-600 transition-colors" />
                </div>
              )}
              <div>
                <label className="text-zinc-500 text-xs uppercase tracking-wider mb-1.5 block">Email</label>
                <input type="email" placeholder="john@example.com" value={formData.email}
                  onChange={e => setFormData({ ...formData, email: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-emerald-600 transition-colors" />
              </div>
              <div>
                <label className="text-zinc-500 text-xs uppercase tracking-wider mb-1.5 block">Password</label>
                <input type="password" placeholder="••••••••" value={formData.password}
                  onChange={e => setFormData({ ...formData, password: e.target.value })}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-emerald-600 transition-colors" />
              </div>
            </div>

            <button onClick={handleAuth} disabled={loading}
              className="w-full mt-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white text-sm font-medium rounded-lg transition-colors duration-150">
              {loading ? "Processing..." : isLogin ? "Sign In" : "Create Account"}
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
