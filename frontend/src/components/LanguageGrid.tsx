"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { GravityButton } from "./GravityButton";

const LANGUAGES = [
  { id: "en", name: "English", native: "English" },
  { id: "hi", name: "Hindi", native: "हिन्दी" },
  { id: "kn", name: "Kannada", native: "ಕನ್ನಡ" },
  { id: "te", name: "Telugu", native: "తెలుగు" },
  { id: "mr", name: "Marathi", native: "मराठी" },
];

export function LanguageGrid() {
  const router = useRouter();
  return (
    <div className="w-full flex-1 flex flex-col pt-8">
      {/* Top Section */}
      <div className="px-6 mb-10 text-center">
        <motion.h1 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-heading font-extrabold text-charcoal mb-3 tracking-tight leading-[1.1]"
        >
          Choose your <br/> language
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-sm font-medium text-charcoal/60"
        >
          Please select your preferred language
        </motion.p>
      </div>

      {/* White Overlapping Card */}
      <motion.div
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className="flex-1 bg-white w-full rounded-t-[40px] shadow-[0_-15px_40px_rgba(0,0,0,0.08)] p-6 sm:p-10 flex flex-col items-center mt-auto min-h-[60vh]"
      >
        <div className="w-full max-w-lg grid grid-cols-2 gap-4 pb-12">
          {LANGUAGES.map((lang, idx) => (
            <motion.div
              key={lang.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 * idx }}
            >
              <GravityButton onClick={() => router.push("/welcome")}>
                <span className="font-bold text-lg text-black">{lang.name}</span>
                <span className="text-xs text-gray-400 font-bold uppercase tracking-wider">
                  {lang.native}
                </span>
              </GravityButton>
            </motion.div>
          ))}
        </div>

        {/* Mock Android Navigation Bar */}
        <div className="mt-auto w-full flex justify-around items-center pt-2 pb-2 opacity-10">
          <div className="w-4 h-4 border-2 border-charcoal rotate-45 rounded-[2px]"></div>
          <div className="w-5 h-5 border-2 border-charcoal rounded-full"></div>
          <div className="w-4 h-4 border-2 border-charcoal rounded-[2px]"></div>
        </div>
      </motion.div>
    </div>
  );
}
