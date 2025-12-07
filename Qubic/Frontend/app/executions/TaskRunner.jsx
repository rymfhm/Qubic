"use client";
import { useState } from "react";
import apiClient from "@/lib/api";

export default function TaskRunner({ agents, onRunTask }) {
  const [task, setTask] = useState("");
  const [selectedAgent, setSelectedAgent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRun = async () => {
    if (!task) return;
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.startTask({
        task_type: "monitor_wallet",
        wallet_address: "0x1234567890abcdef",
        description: task,
      });
      
      onRunTask({ agent: selectedAgent || "default", task, result });
      setTask("");
    } catch (err) {
      setError(err.message || "Failed to start task");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 p-4 border rounded">
      <h2 className="text-lg font-semibold">Run Task</h2>
      <select
        value={selectedAgent}
        onChange={(e) => setSelectedAgent(e.target.value)}
        className="w-full p-2 border rounded"
      >
        <option value="" className="bg-gray-500">Select Agent</option>
        {agents.map((a, idx) => (
          <option className="bg-gray-500 " key={idx} value={a.name}>
            {a.name} ({a.role})
          </option>
        ))}
      </select>
      <input
        type="text"
        placeholder="Enter task description"
        value={task}
        onChange={(e) => setTask(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <button
        onClick={handleRun}
        disabled={loading}
        className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
      >
        {loading ? "Starting..." : "Run Task"}
      </button>
      {error && (
        <div className="p-2 bg-red-100 text-red-700 rounded text-sm">
          {error}
        </div>
      )}
    </div>
  );
}