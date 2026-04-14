"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import React from "react";

interface GravityButtonProps extends React.ComponentProps<typeof Button> {
  children: React.ReactNode;
}

export function GravityButton({ children, className, ...props }: GravityButtonProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -2 }}
      whileTap={{ scale: 0.98 }}
      animate={{
        y: [0, -1, 0],
      }}
      transition={{
        y: {
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        },
        scale: {
          type: "spring",
          stiffness: 400,
          damping: 10,
        },
      }}
      className={cn("w-full", className)}
    >
      <Button
        className={cn(
          "w-full h-[110px] bg-secondary hover:bg-tertiary text-primary border-none rounded-[40px] shadow-sm hover:shadow-md transition-shadow flex flex-col items-center justify-center gap-2",
          className
        )}
        variant="secondary"
        {...props}
      >
        {children}
      </Button>
    </motion.div>
  );
}
