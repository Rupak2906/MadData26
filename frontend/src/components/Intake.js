"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

const steps = ["Basic Info", "Body Metrics", "Training", "Lifestyle", "Goals", "Photos"];

export default function Intake() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [photo, setPhoto] = useState(null);
  const [backPhoto, setBackPhoto] = useState(null);
  const [formData, setFormData] = useState({
    biological_sex: "",
    age: "",
    height_cm: "",
    weight_kg: "",
    experience_level: "",
    days_available: "",
    skip_frequency: "",
    sleep_hours: "",
    stress_level: "",
    diet_strictness: "",
    dietary_preference: "",
    primary_goal: "",
    ideal_physique: "",
  });

  const update = (field, value) => setFormData(prev => ({ ...prev, [field]: value }));

  const OptionButton = ({ field, value, label }) => (
    <button
      onClick={() => update(field, value)}
      className={`px-4 py-2.5 rounded-lg border text-xs font-medium uppercase tracking-wide transition-all duration-150 ${
        formData[field] === value
          ? "bg-emerald-600 border-emerald-600 text-white"
          : "bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200"
      }`}
    >
      {label}
    </button>
  );

  const handleSubmit = async () => {
    try {
      const data = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        data.append(key, value);
      });
      if (photo) data.append("front_photo", photo);
      if (backPhoto) data.append("back_photo", backPhoto);
      const userId = localStorage.getItem("user_id");
      if (userId) data.append("user_id", userId);
      localStorage.setItem("intake_data", JSON.stringify(formData));
      router.push("/analyzing");
    } catch (err) {
      router.push("/analyzing");
    }
  };

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <div className="space-y-6">
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">Biological Sex</label>
              <div className="flex gap-3">
                <OptionButton field="biological_sex" value="male" label="Male" />
                <OptionButton field="biological_sex" value="female" label="Female" />
              </div>
            </div>
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-2 block">Age</label>
              <input
                type="number" placeholder="25"
                value={formData.age}
                onChange={e => update("age", e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-600 transition-colors"
              />
            </div>
          </div>
        );

      case 1:
        return (
          <div className="space-y-4">
            <p className="text-zinc-600 text-xs border-l border-zinc-700 pl-3">
              Body composition and additional dimensions are extracted automatically via computer vision analysis of uploaded photos.
            </p>
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-2 block">Height (cm)</label>
              <input
                type="number" placeholder="175"
                value={formData.height_cm}
                onChange={e => update("height_cm", e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-600 transition-colors"
              />
            </div>
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-2 block">Weight (kg)</label>
              <input
                type="number" placeholder="75"
                value={formData.weight_kg}
                onChange={e => update("weight_kg", e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-600 transition-colors"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">Training Experience</label>
              <div className="flex flex-wrap gap-2">
                <OptionButton field="experience_level" value="beginner" label="Beginner" />
                <OptionButton field="experience_level" value="intermediate" label="Intermediate" />
                <OptionButton field="experience_level" value="advanced" label="Advanced" />
              </div>
            </div>
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">Sessions Per Week</label>
              <div className="flex flex-wrap gap-2">
                {[1, 2, 3, 4, 5, 6].map(d => (
                  <OptionButton key={d} field="days_available" value={String(d)} label={`${d}`} />
                ))}
              </div>
            </div>
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">Session Adherence</label>
              <div className="flex flex-wrap gap-2">
                <OptionButton field="skip_frequency" value="never" label="Always complete" />
                <OptionButton field="skip_frequency" value="rarely" label="Rarely skip" />
                <OptionButton field="skip_frequency" value="sometimes" label="Sometimes skip" />
                <OptionButton field="skip_frequency" value="often" label="Often skip" />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">Average Sleep Duration</label>
              <div className="flex flex-wrap gap-2">
                <OptionButton field="sleep_hours" value="<6hr" label="< 6 hrs" />
                <OptionButton field="sleep_hours" value="6-7hr" label="6–7 hrs" />
                <OptionButton field="sleep_hours" value="7-8hr" label="7–8 hrs" />
                <OptionButton field="sleep_hours" value="8hr+" label="8+ hrs" />
              </div>
            </div>
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">Stress Load</label>
              <div className="flex flex-wrap gap-2">
                <OptionButton field="stress_level" value="low" label="Low" />
                <OptionButton field="stress_level" value="moderate" label="Moderate" />
                <OptionButton field="stress_level" value="high" label="High" />
              </div>
            </div>
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">Dietary Discipline</label>
              <div className="flex flex-wrap gap-2">
                <OptionButton field="diet_strictness" value="loose" label="Flexible" />
                <OptionButton field="diet_strictness" value="moderate" label="Moderate" />
                <OptionButton field="diet_strictness" value="strict" label="Strict" />
              </div>
            </div>
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">Dietary Protocol</label>
              <div className="flex flex-wrap gap-2">
                <OptionButton field="dietary_preference" value="none" label="Standard" />
                <OptionButton field="dietary_preference" value="vegetarian" label="Vegetarian" />
                <OptionButton field="dietary_preference" value="vegan" label="Vegan" />
                <OptionButton field="dietary_preference" value="keto" label="Ketogenic" />
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">Primary Objective</label>
              <div className="flex flex-wrap gap-2">
                <OptionButton field="primary_goal" value="build_muscle" label="Hypertrophy" />
                <OptionButton field="primary_goal" value="lose_fat" label="Fat Reduction" />
                <OptionButton field="primary_goal" value="both" label="Recomposition" />
              </div>
            </div>
            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">Target Physique Profile</label>
              <div className="grid grid-cols-2 gap-2">
                <OptionButton field="ideal_physique" value="lean_athletic" label="Lean Athletic" />
                <OptionButton field="ideal_physique" value="muscular" label="Muscular" />
                <OptionButton field="ideal_physique" value="v_taper" label="V-Taper" />
                <OptionButton field="ideal_physique" value="aesthetic" label="Aesthetic" />
                <OptionButton field="ideal_physique" value="bodybuilder" label="Bodybuilder" />
                <OptionButton field="ideal_physique" value="powerlifter" label="Powerlifter" />
                <OptionButton field="ideal_physique" value="slim_fit" label="Slim Fit" />
                <OptionButton field="ideal_physique" value="classic_physique" label="Classic" />
                <OptionButton field="ideal_physique" value="athletic_bulk" label="Athletic Bulk" />
                <OptionButton field="ideal_physique" value="toned" label="Toned" />
              </div>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <p className="text-zinc-600 text-xs border-l border-zinc-700 pl-3 leading-relaxed">
              Computer vision model extracts shoulder width, waist-to-hip ratio, limb proportions, and structural frame classification from these images.
            </p>

            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">
                Anterior View
                <span className="text-zinc-600 ml-2 normal-case">Stand neutral, arms at sides</span>
              </label>
              <div
                onClick={() => document.getElementById("front-photo").click()}
                className="border border-dashed border-zinc-700 hover:border-emerald-600 rounded-xl p-8 text-center cursor-pointer transition-colors duration-150"
              >
                {photo ? (
                  <img src={URL.createObjectURL(photo)} alt="front"
                    className="max-h-48 mx-auto rounded-lg object-cover"
                  />
                ) : (
                  <div>
                    <p className="text-zinc-500 text-sm mb-1">Upload anterior photo</p>
                    <p className="text-zinc-600 text-xs">Full body, front facing</p>
                  </div>
                )}
              </div>
              <input id="front-photo" type="file" accept="image/*" className="hidden"
                onChange={e => setPhoto(e.target.files[0])}
              />
            </div>

            <div>
              <label className="text-zinc-500 text-xs uppercase tracking-wider mb-3 block">
                Posterior View
                <span className="text-zinc-600 ml-2 normal-case">Same position, facing away</span>
              </label>
              <div
                onClick={() => document.getElementById("back-photo").click()}
                className="border border-dashed border-zinc-700 hover:border-emerald-600 rounded-xl p-8 text-center cursor-pointer transition-colors duration-150"
              >
                {backPhoto ? (
                  <img src={URL.createObjectURL(backPhoto)} alt="back"
                    className="max-h-48 mx-auto rounded-lg object-cover"
                  />
                ) : (
                  <div>
                    <p className="text-zinc-500 text-sm mb-1">Upload posterior photo</p>
                    <p className="text-zinc-600 text-xs">Full body, back facing</p>
                  </div>
                )}
              </div>
              <input id="back-photo" type="file" accept="image/*" className="hidden"
                onChange={e => setBackPhoto(e.target.files[0])}
              />
            </div>
          </div>
        );
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-white">

      {/* Top bar */}
      <div className="border-b border-zinc-800 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="text-zinc-400 text-xs uppercase tracking-widest font-medium">Input Collection</span>
        </div>
        <span className="text-zinc-600 text-xs">Step {step + 1} / {steps.length} — {steps[step]}</span>
      </div>

      <div className="max-w-lg mx-auto px-6 py-10">

        {/* Progress */}
        <div className="mb-8">
          <div className="h-px bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-600 rounded-full transition-all duration-500"
              style={{ width: `${((step + 1) / steps.length) * 100}%` }}
            />
          </div>
          <div className="flex justify-between mt-2">
            {steps.map((s, i) => (
              <span key={s} className={`text-xs ${i === step ? "text-emerald-500" : i < step ? "text-zinc-500" : "text-zinc-700"}`}>
                {s}
              </span>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="mb-10 min-h-[300px]">
          {renderStep()}
        </div>

        {/* Navigation */}
        <div className="fixed bottom-0 left-0 right-0 bg-zinc-950 border-t border-zinc-800 px-6 py-4">
          <div className="max-w-lg mx-auto flex gap-3">
            {step > 0 ? (
              <button
                onClick={() => setStep(s => s - 1)}
                className="w-28 py-2.5 border border-zinc-700 hover:border-zinc-500 text-zinc-400 hover:text-zinc-200 rounded-lg text-xs font-medium uppercase tracking-wide transition-colors"
              >
                ← Back
              </button>
            ) : (
              <div className="w-28" />
            )}
            <button
              onClick={() => step < steps.length - 1 ? setStep(s => s + 1) : handleSubmit()}
              className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-medium uppercase tracking-wide transition-colors"
            >
              {step < steps.length - 1 ? "Continue →" : "Run Analysis"}
            </button>
          </div>
        </div>

        <div className="h-24" />
      </div>
    </main>
  );
}