"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const analysisSteps = [
  { id: 1, text: "Uploading image data", duration: 1500 },
  { id: 2, text: "Running pose estimation", duration: 2000 },
  { id: 3, text: "Extracting body dimensions", duration: 2000 },
  { id: 4, text: "Classifying structural frame", duration: 1500 },
  { id: 5, text: "Calculating FFMI and lean mass index", duration: 1500 },
  { id: 6, text: "Running ML prediction model", duration: 2000 },
  { id: 7, text: "Generating adaptation projections", duration: 1500 },
  { id: 8, text: "Building nutrition targets", duration: 1000 },
  { id: 9, text: "Finalizing output", duration: 1000 },
];

export default function Analyzing() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    let stepIndex = 0;
    let totalElapsed = 0;
    const totalDuration = analysisSteps.reduce((sum, s) => sum + s.duration, 0);

    const runStep = () => {
      if (stepIndex >= analysisSteps.length) {
        setDone(true);
        setProgress(100);
        setTimeout(() => router.push("/dashboard"), 1000);
        return;
      }

      setCurrentStep(stepIndex);
      const step = analysisSteps[stepIndex];
      const stepEnd = totalElapsed + step.duration;

      const interval = setInterval(() => {
        const now = Date.now() - startTime;
        const pct = Math.min((now / totalDuration) * 100, 100);
        setProgress(Math.round(pct));
      }, 50);

      setTimeout(() => {
        clearInterval(interval);
        setCompletedSteps(prev => [...prev, stepIndex]);
        totalElapsed = stepEnd;
        stepIndex++;
        runStep();
      }, step.duration);
    };

    const startTime = Date.now();
    runStep();
  }, []);

  return (
    <main className="min-h-screen bg-zinc-950 text-white flex flex-col">

      {/* Top bar */}
      <div className="border-b border-zinc-800 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${done ? "bg-emerald-500" : "bg-emerald-500 animate-pulse"}`} />
          <span className="text-zinc-400 text-xs uppercase tracking-widest font-medium">
            {done ? "Analysis Complete" : "Processing"}
          </span>
        </div>
        <span className="text-zinc-600 text-xs">{progress}%</span>
      </div>

      <div className="flex flex-col items-center justify-center flex-1 px-6">
        <div className="w-full max-w-md">

          {/* Header */}
          <div className="mb-8">
            <p className="text-zinc-500 text-xs uppercase tracking-widest mb-2">
              {done ? "Complete" : "Running Analysis"}
            </p>
            <h1 className="text-2xl font-semibold text-zinc-100">
              {done ? "Model output ready" : "Analyzing anthropometric data"}
            </h1>
            {!done && (
              <p className="text-zinc-500 text-sm mt-1">
                {analysisSteps[currentStep]?.text}...
              </p>
            )}
          </div>

          {/* Progress bar */}
          <div className="mb-8">
            <div className="h-px bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-600 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Steps list */}
          <div className="space-y-2">
            {analysisSteps.map((step, index) => {
              const isCompleted = completedSteps.includes(index);
              const isCurrent = currentStep === index && !isCompleted;
              const isPending = index > currentStep;

              return (
                <div
                  key={step.id}
                  className={`flex items-center gap-3 py-2 transition-all duration-300 ${
                    isPending ? "opacity-25" : ""
                  }`}
                >
                  <div className={`w-4 h-4 rounded-sm flex items-center justify-center flex-shrink-0 text-xs border transition-colors ${
                    isCompleted ? "bg-emerald-600 border-emerald-600 text-white" :
                    isCurrent ? "border-emerald-600 text-emerald-500" :
                    "border-zinc-700 text-zinc-600"
                  }`}>
                    {isCompleted ? "✓" : isCurrent ? (
                      <span className="animate-pulse">·</span>
                    ) : ""}
                  </div>

                  <span className={`text-xs ${
                    isCompleted ? "text-zinc-500 line-through" :
                    isCurrent ? "text-zinc-200" :
                    "text-zinc-600"
                  }`}>
                    {step.text}
                  </span>

                  {isCurrent && (
                    <div className="ml-auto w-3 h-3 border border-emerald-600 border-t-transparent rounded-full animate-spin" />
                  )}
                </div>
              );
            })}
          </div>

          {done && (
            <p className="text-zinc-500 text-xs mt-8 text-center">
              Redirecting to results...
            </p>
          )}
        </div>
      </div>
    </main>
  );
}