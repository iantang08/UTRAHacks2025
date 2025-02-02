import Link from "next/link"
import { motion } from "framer-motion"

export default function Home() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen flex flex-col items-center justify-center bg-gray-100 text-black"
    >
      <h1 className="text-4xl font-bold mb-4">Exercise Tracker</h1>
      <h2 className="text-xl mb-8">By John Doe and Jane Smith</h2>
      <Link href="/tutorial">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          GO!
        </motion.button>
      </Link>
    </motion.div>
  )
}

