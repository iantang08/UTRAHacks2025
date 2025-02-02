"use client"

import { useRouter } from "next/navigation"
import { motion } from "framer-motion"

export default function Exercise({ params }: { params: { name: string } }) {
  const router = useRouter()
  const decodedName = decodeURIComponent(params.name)

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen flex flex-col items-center justify-center bg-gray-100 text-black"
    >
      <h1 className="text-3xl font-bold mb-8">{decodedName}</h1>
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => router.push("/home")}
        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        Back to Home
      </motion.button>
    </motion.div>
  )
}

