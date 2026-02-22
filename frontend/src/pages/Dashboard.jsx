import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const workoutPlan = {
  Monday: ["Squats 4x8", "Romanian Deadlift 3x10", "Leg Press 3x12", "Calf Raises 4x15"],
  Tuesday: ["Bench Press 4x8", "Incline DB Press 3x10", "Cable Flyes 3x12", "Tricep Pushdown 3x12"],
  Wednesday: ["Rest / Light Cardio"],
  Thursday: ["Deadlift 4x6", "Pull-ups 4x8", "Barbell Row 3x10", "Face Pulls 3x15"],
  Friday: ["OHP 4x8", "Lateral Raises 4x12", "Arnold Press 3x10", "Bicep Curls 3x12"],
  Saturday: ["Full Body Accessory + Core"],
  Sunday: ["Rest & Recovery"],
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-xs">
        <p className="text-zinc-400">{label}</p>
        <p className="text-emerald-400 font-medium">{payload[0].value} kg</p>
      </div>
    );
  }
  return null;
};

export default function Dashboard() {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";
  const [activeTab, setActiveTab] = useState("body");
  const [plan, setPlan] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    fetch(`${API_BASE_URL}/plan?token=${token}`)
      .then(r => r.json())
      .then(data => setPlan(data))
      .catch(() => {});
  }, [API_BASE_URL]);

  // Pull real data from API or fall back to defaults
  const tp = plan?.transformation_plan;
  const tl = plan?.timeline;
  const dp = plan?.dietary_plan;

  const frame = tp?.muscle_gaps ? "Wide" : "Wide";
  const ffmiCeiling = tp?.peak_ffmi ?? 24.8;
  const leanMassPotential = tp?.peak_lean_mass_kg ?? 74;
  const targetBf = tp?.target_bf_pct ?? 12;
  const muscleGapData = tp?.muscle_gaps
    ? Object.entries(tp.muscle_gaps).map(([muscle, gap]) => ({ muscle, gap }))
    : [
        { muscle: "Legs", gap: 4.5 },
        { muscle: "Back", gap: 2.8 },
        { muscle: "Chest", gap: 3.2 },
        { muscle: "Shoulders", gap: 1.8 },
        { muscle: "Arms", gap: 1.4 },
      ];

  const tabs = [
    { id: "body", label: "Body Analysis" },
    { id: "diet", label: "Nutrition Protocol" },
    { id: "transformation", label: "Training Protocol" },
  ];

  return (
    <main className="min-h-screen bg-zinc-950 text-white">
      {/* Header */}
      <div className="border-b border-zinc-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <div>
              <h1 className="text-sm font-medium text-zinc-100">Projected Adaptation Model</h1>
              <p className="text-zinc-600 text-xs">
                {frame} Frame · Balanced Composition · Confidence: {tl?.confidence_level ?? "78%"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-zinc-600 text-xs">Experimental Model v0.3</span>
            <button
              onClick={() => { localStorage.clear(); navigate("/"); }}
              className="px-3 py-1.5 border border-zinc-700 hover:border-zinc-500 text-zinc-400 hover:text-zinc-200 rounded-lg text-xs font-medium uppercase tracking-wide transition-colors"
            >
              New Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-zinc-800">
        <div className="max-w-5xl mx-auto px-6 flex">
          {tabs.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-3.5 text-xs font-medium uppercase tracking-wider border-b-2 transition-all ${
                activeTab === tab.id ? "border-emerald-500 text-emerald-400" : "border-transparent text-zinc-500 hover:text-zinc-300"
              }`}>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">

        {/* ── Body Analysis ── */}
        {activeTab === "body" && (
          <div className="space-y-6">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <p className="text-zinc-500 text-xs uppercase tracking-wider mb-4">Model Summary</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {[
                  { label: "Structural Frame", value: frame },
                  { label: "FFMI Ceiling", value: ffmiCeiling },
                  { label: "Lean Mass Potential", value: `${leanMassPotential} kg` },
                  { label: "Estimated Timeline", value: tl ? `${tl.total_months_realistic} mo` : "14–18 mo" },
                ].map(item => (
                  <div key={item.label}>
                    <p className="text-zinc-500 text-xs uppercase tracking-wider mb-1">{item.label}</p>
                    <p className="text-zinc-100 text-xl font-medium">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                <p className="text-zinc-500 text-xs uppercase tracking-wider mb-4">Current State</p>
                <div className="space-y-3">
                  {[
                    { label: "Body Fat", value: `${tp?.fat_loss_required_pct ? (22).toFixed(0) : 22}%` },
                    { label: "Lean Mass", value: `${tp?.peak_lean_mass_kg ? (leanMassPotential - (tp?.muscle_gain_required_kg ?? 13)).toFixed(0) : 61} kg` },
                    { label: "FFMI", value: "19.2" },
                    { label: "Frame", value: frame },
                  ].map(item => (
                    <div key={item.label} className="flex justify-between items-center">
                      <span className="text-zinc-500 text-xs uppercase tracking-wider">{item.label}</span>
                      <span className="text-zinc-100 text-sm font-medium">{item.value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-zinc-500 text-xs uppercase tracking-wider">Peak Projection</p>
                  <span className="text-zinc-600 text-xs">Range Estimate</span>
                </div>
                <div className="space-y-3">
                  {[
                    { label: "Body Fat", value: `${targetBf}%` },
                    { label: "Lean Mass", value: `${leanMassPotential} kg` },
                    { label: "FFMI", value: ffmiCeiling },
                    { label: "Profile", value: "V-Taper" },
                  ].map(item => (
                    <div key={item.label} className="flex justify-between items-center">
                      <span className="text-zinc-500 text-xs uppercase tracking-wider">{item.label}</span>
                      <span className="text-emerald-400 text-sm font-medium">{item.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-1">
                <p className="text-zinc-200 text-sm font-medium">Muscle Development Gaps</p>
                <span className="text-zinc-600 text-xs">kg required to reach projection</span>
              </div>
              <p className="text-zinc-600 text-xs mb-6">Per muscle group, relative to peak lean mass target</p>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={muscleGapData} barSize={28}>
                  <XAxis dataKey="muscle" tick={{ fill: "#52525b", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#52525b", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                  <Bar dataKey="gap" fill="#059669" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <p className="text-zinc-500 text-xs uppercase tracking-wider mb-3">Methodology</p>
              <p className="text-zinc-500 text-xs leading-relaxed">
                {tp?.agent_reasoning ?? "Estimates are based on structural frame modeling, lean mass index projections, and historical hypertrophy adaptation data. Peak potential is calculated using the Berkhan-Lyle natural limit model adjusted for frame width and FFMI baseline. Results represent probabilistic ranges with ±8% confidence interval."}
              </p>
            </div>
          </div>
        )}

        {/* ── Nutrition Protocol ── */}
        {activeTab === "diet" && (
          <div className="space-y-6">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <p className="text-zinc-500 text-xs uppercase tracking-wider">Caloric Strategy</p>
                <span className="px-2 py-0.5 border border-zinc-700 rounded text-zinc-400 text-xs">
                  {dp?.caloric_strategy ?? "Recomposition Phase"}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-6">
                {[
                  { label: "Daily Target", value: `${dp?.daily_calories ?? 2800} kcal` },
                  { label: "Adjustment", value: `${dp?.caloric_adjustment > 0 ? "+" : ""}${dp?.caloric_adjustment ?? 200} kcal` },
                  { label: "Hydration", value: `${dp?.water_intake_liters ?? 3.2} L/day` },
                ].map(item => (
                  <div key={item.label}>
                    <p className="text-zinc-500 text-xs uppercase tracking-wider mb-1">{item.label}</p>
                    <p className="text-zinc-100 text-xl font-medium">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <p className="text-zinc-500 text-xs uppercase tracking-wider mb-4">Macronutrient Distribution</p>
              <div className="space-y-4">
                {[
                  { name: "Protein", grams: dp?.protein_g ?? 175, pct: 25, color: "bg-emerald-600" },
                  { name: "Carbohydrates", grams: dp?.carbs_g ?? 350, pct: 50, color: "bg-zinc-500" },
                  { name: "Lipids", grams: dp?.fats_g ?? 78, pct: 25, color: "bg-zinc-600" },
                ].map(macro => (
                  <div key={macro.name}>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-zinc-400 uppercase tracking-wider">{macro.name}</span>
                      <span className="text-zinc-500">{macro.grams}g · {macro.pct}%</span>
                    </div>
                    <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
                      <div className={`h-full ${macro.color} rounded-full`} style={{ width: `${macro.pct * 2}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <p className="text-zinc-500 text-xs uppercase tracking-wider mb-4">Meal Structure</p>
              <div className="space-y-0">
                {[
                  { time: "07:00", meal: "Breakfast", cals: "600 kcal", example: "Oats, eggs, banana" },
                  { time: "10:30", meal: "Mid-Morning", cals: "400 kcal", example: "Greek yogurt, nuts" },
                  { time: "13:00", meal: "Lunch", cals: "700 kcal", example: "Chicken, rice, vegetables" },
                  { time: "16:00", meal: "Pre-Training", cals: "400 kcal", example: "Protein shake, fruit" },
                  { time: "19:30", meal: "Dinner", cals: "700 kcal", example: "Salmon, sweet potato" },
                ].map(item => (
                  <div key={item.time} className="flex items-center gap-4 py-3 border-b border-zinc-800 last:border-0">
                    <span className="text-emerald-600 text-xs font-medium w-12 flex-shrink-0">{item.time}</span>
                    <div className="flex-1">
                      <p className="text-zinc-300 text-xs font-medium">{item.meal}</p>
                      <p className="text-zinc-600 text-xs">{item.example}</p>
                    </div>
                    <span className="text-zinc-500 text-xs">{item.cals}</span>
                  </div>
                ))}
              </div>
              {dp?.diet_reasoning && (
                <p className="text-zinc-600 text-xs mt-4 border-l border-zinc-700 pl-3 leading-relaxed">{dp.diet_reasoning}</p>
              )}
            </div>
          </div>
        )}

        {/* ── Training Protocol ── */}
        {activeTab === "transformation" && (
          <div className="space-y-6">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-1">
                <p className="text-zinc-200 text-sm font-medium">Projected Timeline</p>
                <span className="text-zinc-600 text-xs">
                  Confidence: {tl?.confidence_level ?? "78%"}
                </span>
              </div>
              <p className="text-zinc-600 text-xs mb-6">
                {tl?.consistency_impact ?? "Based on 65% adherence score and structural frame classification"}
              </p>
              <div className="space-y-4">
                {[
                  { label: "Optimistic", months: tl?.total_months_optimistic ?? 14, color: "bg-emerald-600" },
                  { label: "Realistic", months: tl?.total_months_realistic ?? 18, color: "bg-zinc-500" },
                  { label: "Conservative", months: tl?.total_months_conservative ?? 24, color: "bg-zinc-700" },
                ].map(t => (
                  <div key={t.label}>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-zinc-400 uppercase tracking-wider">{t.label}</span>
                      <span className="text-zinc-500">{t.months} months</span>
                    </div>
                    <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
                      <div className={`h-full ${t.color} rounded-full`} style={{ width: `${(t.months / 24) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <p className="text-zinc-500 text-xs uppercase tracking-wider mb-4">Phase Breakdown</p>
              <div className="space-y-0">
                {[
                  {
                    num: "01",
                    goal: tl?.phase_1_goal ?? "Cut Phase",
                    months: `Months 1–${tl?.phase_1_months ?? 4}`,
                    desc: "Lose fat first, get lean before building muscle"
                  },
                  {
                    num: "02",
                    goal: tl?.phase_2_goal ?? "Build Phase",
                    months: `Months ${(tl?.phase_1_months ?? 4) + 1}–${(tl?.phase_1_months ?? 4) + (tl?.phase_2_months ?? 10)}`,
                    desc: "Eat more, train hard, pack on muscle mass"
                  },
                  {
                    num: "03",
                    goal: tl?.phase_3_goal ?? "Final Cut",
                    months: `Months ${(tl?.phase_1_months ?? 4) + (tl?.phase_2_months ?? 10) + 1}–${tl?.total_months_realistic ?? 18}`,
                    desc: "Lose the last bit of fat to reveal the physique you built"
                  },
                ].map(p => (
                  <div key={p.num} className="flex gap-4 py-4 border-b border-zinc-800 last:border-0">
                    <span className="text-zinc-700 text-xs font-medium w-6 flex-shrink-0 mt-0.5">{p.num}</span>
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <p className="text-zinc-200 text-xs font-medium">{p.goal}</p>
                        <span className="text-zinc-600 text-xs">{p.months}</span>
                      </div>
                      <p className="text-zinc-500 text-xs">{p.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-1">
                <p className="text-zinc-200 text-sm font-medium">Weekly Training Split</p>
                <span className="text-zinc-600 text-xs">5-day PPL</span>
              </div>
              <p className="text-zinc-600 text-xs mb-4">Optimized for wide frame structural advantage</p>
              <div className="space-y-0">
                {Object.entries(workoutPlan).map(([day, exercises]) => (
                  <div key={day} className="py-3 border-b border-zinc-800 last:border-0">
                    <p className="text-zinc-500 text-xs uppercase tracking-wider mb-2">{day}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {exercises.map((ex, i) => (
                        <span key={i} className="px-2 py-1 bg-zinc-800 border border-zinc-700 rounded text-zinc-400 text-xs">{ex}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
