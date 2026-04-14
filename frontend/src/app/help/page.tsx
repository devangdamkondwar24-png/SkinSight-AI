"use client";

import { motion } from "framer-motion";
import { HelpCircle, ArrowLeft, MessageSquare, Mail, PhoneCall } from "lucide-react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-stone-50 font-['Plus_Jakarta_Sans',_sans-serif]">
      <Navbar />
      
      <main className="pt-32 pb-20 px-16 max-w-4xl mx-auto text-center">
        <Link 
          href="/analysis" 
          className="inline-flex items-center gap-2 text-stone-400 hover:text-[#004d40] transition-colors mb-8 text-sm font-bold group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Back to Dashboard
        </Link>
        
        <div className="w-20 h-20 bg-[#004d40]/5 rounded-[2rem] flex items-center justify-center text-[#004d40] mx-auto mb-8">
          <HelpCircle className="w-10 h-10" />
        </div>
        
        <h1 className="text-5xl font-black text-[#004d40] tracking-tight mb-4">
          How can we help you?
        </h1>
        <p className="text-stone-500 font-medium text-lg mb-12">
          We're here to support your skin journey. Explore our support channels below.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { icon: MessageSquare, title: "Live Chat", desc: "Average response: 5 mins", color: "emerald" },
            { icon: Mail, title: "Email Support", desc: "SkinSights@help.com", color: "blue" },
            { icon: PhoneCall, title: "Phone Support", desc: "+1 (800) SKINSIGHT", color: "stone" }
          ].map((item, idx) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-white p-8 rounded-[2rem] border border-stone-100 shadow-xl shadow-stone-200/30 text-center hover:scale-105 transition-all cursor-pointer group"
            >
              <div className={`w-12 h-12 bg-stone-50 rounded-xl flex items-center justify-center text-stone-400 mx-auto mb-4 group-hover:bg-[#004d40]/10 group-hover:text-[#004d40] transition-all`}>
                <item.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-black text-[#004d40] mb-2">{item.title}</h3>
              <p className="text-stone-400 text-sm font-medium">{item.desc}</p>
            </motion.div>
          ))}
        </div>
        
        <div className="mt-20 p-12 bg-white rounded-[3rem] border border-stone-100 text-left">
          <h2 className="text-2xl font-black text-[#004d40] mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            {[
              { q: "How accurate is the skin analysis?", a: "SkinSight uses high-precision computer vision and YOLOv8 models trained on clinical datasets to achieve clinical-grade screening accuracy." },
              { q: "Is my data private?", a: "Yes, all analysis is performed locally or via secure encrypted channels, and your data is only visible to you." }
            ].map(faq => (
              <div key={faq.q}>
                <h4 className="font-bold text-[#004d40] mb-2">{faq.q}</h4>
                <p className="text-stone-500 text-sm leading-relaxed">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
