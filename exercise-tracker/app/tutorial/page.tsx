import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"

export default function Tutorial() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen flex flex-col items-center justify-center bg-gray-100 text-black p-8"
    >
      <h1 className="text-3xl font-bold mb-4">Tutorial</h1>
      <p className="mb-4 max-w-2xl text-center">
        Welcome to the Exercise Tracker! This app helps you keep track of your exercises. You can add exercises, remove
        them, and track your progress over time.
      </p>
      <Image src="/placeholder.svg" alt="Exercise Tracker Tutorial" width={400} height={300} className="mb-8" />
      <Link href="/home">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        >
          START
        </motion.button>
      </Link>
    </motion.div>
  )
}

