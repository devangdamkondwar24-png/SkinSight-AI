"use client";

import { motion } from "framer-motion";
import { GravityButton } from "@/components/GravityButton";
import { Navbar } from "@/components/Navbar";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function WelcomePage() {
  const router = useRouter();

  return (
    <main className="min-h-screen bg-mint flex flex-col items-center">
      {/* Background Neural Orbs */}
      <div className="fixed inset-0 overflow-hidden -z-10 opacity-30 pointer-events-none">
        <div className="absolute top-[-5%] left-[-5%] w-[50%] h-[50%] bg-white filter blur-[100px] rounded-full" />
        <div className="absolute bottom-[15%] right-[-5%] w-[40%] h-[40%] bg-[#D1E8E2] filter blur-[80px] rounded-full" />
      </div>

      <div className="w-full max-w-none min-h-screen flex flex-col relative overflow-hidden bg-surface shadow-2xl">
        <Navbar />
        
        <div className="flex-1 flex flex-col">
          {/* Hero Section with Premium Image */}
          <div className="relative w-full h-[45vh] overflow-hidden">
            <motion.div 
              initial={{ scale: 1.1, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 1.2, ease: "easeOut" }}
              className="w-full h-full relative"
            >
              <img 
                src="https://images.unsplash.com/photo-1612817288484-6f916006741a?q=80&w=2070&auto=format&fit=crop" 
                alt="Clinical Skincare"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-surface" />
            </motion.div>
            
            {/* Floating Glass Brand Label */}
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="absolute top-8 left-8 bg-white/40 backdrop-blur-xl px-6 py-2 rounded-full border border-white/20 shadow-lg"
            >
              <span className="text-charcoal font-black tracking-tighter text-sm uppercase">Laboratory Certified</span>
            </motion.div>
          </div>

          {/* Content Area */}
          <div className="px-8 -mt-12 relative z-10">
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="space-y-4"
            >
              <h1 className="text-6xl font-heading font-black text-charcoal tracking-tighter leading-[0.9]">
                Skin Sight
              </h1>
              <p className="text-xl font-body font-bold text-charcoal/40 leading-tight">
                your skin expert
              </p>
            </motion.div>

            {/* Feature Pills */}
            <div className="flex gap-2 mt-8 overflow-x-auto pb-4 no-scrollbar">
              {["AI Analysis", "Dermatology", "Clinical", "Ethereal"].map((tag) => (
                <span key={tag} className="px-5 py-2 bg-mint/20 text-charcoal/60 rounded-full text-xs font-bold whitespace-nowrap">
                  {tag}
                </span>
              ))}
            </div>

            <motion.div
              initial={{ y: 40, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6, type: "spring" }}
              className="pt-10"
            >
              <GravityButton 
                onClick={() => router.push("/login")}
                className="bg-charcoal text-white hover:bg-charcoal/90 h-[72px] shadow-xl group max-w-[320px] mx-auto"
              >
                <div className="flex items-center justify-center gap-3 w-full">
                  <span className="text-xl font-black">Get Started</span>
                  <motion.span
                    animate={{ x: [0, 5, 0] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  >
                    →
                  </motion.span>
                </div>
              </GravityButton>
            </motion.div>

            <p className="text-[10px] text-center text-charcoal/20 mt-8 font-bold uppercase tracking-widest px-8">
              Premium Digital Dermatology • v2.0
            </p>
          </div>

          {/* Bottom Sheet Detail */}
          <div className="mt-auto pb-8 px-8 flex justify-between items-center opacity-10">
            <div className="w-12 h-1 bg-charcoal rounded-full" />
            <div className="w-12 h-1 bg-charcoal rounded-full" />
            <div className="w-12 h-1 bg-charcoal rounded-full" />
          </div>
        </div>
      </div>
    </main>
  );
}
