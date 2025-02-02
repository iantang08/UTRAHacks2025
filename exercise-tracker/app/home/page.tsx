"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"

export default function Home() {
  const [exercises, setExercises] = useState<string[]>([])
  const [newExercise, setNewExercise] = useState("")
  const [error, setError] = useState("")

  useEffect(() => {
    const savedExercises = localStorage.getItem("exercises")
    if (savedExercises) {
      setExercises(JSON.parse(savedExercises))
    }
  }, [])

  useEffect(() => {
    localStorage.setItem("exercises", JSON.stringify(exercises))
  }, [exercises])

  const addExercise = () => {
    const trimmedExercise = newExercise.trim()
    if (trimmedExercise !== "") {
      if (exercises.includes(trimmedExercise)) {
        setError("This exercise already exists!")
      } else {
        setExercises([...exercises, trimmedExercise])
        setNewExercise("")
        setError("")
      }
    }
  }

  const removeExercise = (index: number) => {
    setExercises(exercises.filter((_, i) => i !== index))
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen flex flex-col items-center justify-center bg-gray-100 text-black p-8"
    >
      <h1 className="text-3xl font-bold mb-8">Exercise Tracker</h1>
      <div className="mb-4">
        <input
          type="text"
          value={newExercise}
          onChange={(e) => setNewExercise(e.target.value)}
          className="border rounded px-2 py-1 mr-2 text-black"
          placeholder="New exercise"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={addExercise}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded"
        >
          Add Exercise
        </motion.button>
      </div>
      <AnimatePresence>
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="text-red-500 mb-4"
          >
            {error}
          </motion.p>
        )}
      </AnimatePresence>
      <ul className="space-y-2">
        <AnimatePresence>
          {exercises.map((exercise, index) => (
            <motion.li
              key={exercise}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex items-center"
            >
              <Link href={`/exercise/${encodeURIComponent(exercise)}`}>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-1 px-2 rounded mr-2"
                >
                  {exercise}
                </motion.button>
              </Link>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => removeExercise(index)}
                className="bg-red-600 hover:bg-red-700 text-white font-bold py-1 px-2 rounded"
              >
                Remove
              </motion.button>
            </motion.li>
          ))}
        </AnimatePresence>
      </ul>
    </motion.div>
  )
}

