"use client";
import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import apiClient from "@/lib/api";

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  const [auditLog, setAuditLog] = useState(null);

  const [formData, setFormData] = useState({
    task_type: "monitor_wallet",
    wallet_address: "",
    description: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.startTask({
        task_type: formData.task_type,
        wallet_address: formData.wallet_address || "0x1234567890abcdef",
        description: formData.description || "Monitor wallet balance",
      });

      setTasks((prev) => [result, ...prev]);
      setSelectedTask(result.task_id);
      setFormData({ task_type: "monitor_wallet", wallet_address: "", description: "" });
    } catch (err) {
      setError(err.message || "Failed to start task");
    } finally {
      setLoading(false);
    }
  };

  const fetchTaskStatus = async (taskId) => {
    try {
      const status = await apiClient.getTaskStatus(taskId);
      setTaskStatus(status);
      
      // Fetch audit log if available
      if (status.status !== "pending") {
        try {
          const audit = await apiClient.getAuditLog(taskId);
          setAuditLog(audit);
        } catch (err) {
          console.warn("Could not fetch audit log:", err);
        }
      }
    } catch (err) {
      setError(err.message || "Failed to fetch task status");
    }
  };

  const handleApprove = async (taskId, approved) => {
    try {
      await apiClient.approveTask(taskId, approved, approved ? "Approved by user" : "Rejected by user");
      await fetchTaskStatus(taskId);
    } catch (err) {
      setError(err.message || "Failed to process approval");
    }
  };

  useEffect(() => {
    if (selectedTask) {
      fetchTaskStatus(selectedTask);
      const interval = setInterval(() => {
        fetchTaskStatus(selectedTask);
      }, 3000); // Poll every 3 seconds

      return () => clearInterval(interval);
    }
  }, [selectedTask]);

  const getStatusColor = (status) => {
    const colors = {
      pending: "bg-yellow-100 text-yellow-800",
      executing: "bg-blue-100 text-blue-800",
      waiting_approval: "bg-orange-100 text-orange-800",
      approved: "bg-green-100 text-green-800",
      rejected: "bg-red-100 text-red-800",
      completed: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <h1 className="text-3xl font-bold">Task Management</h1>

        {/* Create Task Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Create New Task</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Task Type</label>
              <select
                value={formData.task_type}
                onChange={(e) => setFormData({ ...formData, task_type: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                required
              >
                <option value="monitor_wallet">Monitor Wallet</option>
                <option value="transfer_funds">Transfer Funds</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Wallet Address</label>
              <input
                type="text"
                value={formData.wallet_address}
                onChange={(e) => setFormData({ ...formData, wallet_address: e.target.value })}
                placeholder="0x1234567890abcdef"
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Task description"
                className="w-full px-3 py-2 border rounded-md"
                rows={3}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Starting..." : "Start Task"}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
              {error}
            </div>
          )}
        </div>

        {/* Task List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Tasks</h2>
          {tasks.length === 0 ? (
            <p className="text-gray-500">No tasks yet. Create one above.</p>
          ) : (
            <div className="space-y-2">
              {tasks.map((task) => (
                <div
                  key={task.task_id}
                  className={`p-4 border rounded-md cursor-pointer hover:bg-gray-50 ${
                    selectedTask === task.task_id ? "border-blue-500 bg-blue-50" : ""
                  }`}
                  onClick={() => setSelectedTask(task.task_id)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">{task.task_id}</p>
                      <p className="text-sm text-gray-500">{task.message}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-sm ${getStatusColor(task.status)}`}>
                      {task.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Task Details */}
        {selectedTask && taskStatus && (
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-xl font-semibold">Task Details</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Task ID</p>
                <p className="font-mono text-sm">{taskStatus.task_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <span className={`px-2 py-1 rounded text-sm ${getStatusColor(taskStatus.status)}`}>
                  {taskStatus.status}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-500">Current Step</p>
                <p>{taskStatus.current_step || "N/A"} / {taskStatus.total_steps || "N/A"}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Requires Approval</p>
                <p>{taskStatus.requires_approval ? "Yes" : "No"}</p>
              </div>
            </div>

            {taskStatus.requires_approval && taskStatus.status === "waiting_approval" && (
              <div className="p-4 bg-orange-50 border border-orange-200 rounded-md">
                <p className="font-medium mb-2">Approval Required</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleApprove(selectedTask, true)}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => handleApprove(selectedTask, false)}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                  >
                    Reject
                  </button>
                </div>
              </div>
            )}

            {/* Audit Log */}
            {auditLog && (
              <div className="mt-4">
                <h3 className="font-semibold mb-2">Audit Log</h3>
                <div className="space-y-2">
                  {auditLog.logs.map((log, idx) => (
                    <div key={idx} className="p-3 bg-gray-50 rounded-md text-sm">
                      <div className="flex justify-between">
                        <span className="font-medium">Step {log.step_index}: {log.step_type}</span>
                        <span className={getStatusColor(log.status)}>{log.status}</span>
                      </div>
                      {log.qubic_txid && (
                        <p className="text-xs text-gray-500 mt-1">
                          Qubic TX: <span className="font-mono">{log.qubic_txid}</span>
                        </p>
                      )}
                    </div>
                  ))}
                  {auditLog.qubic_txid && (
                    <div className="p-3 bg-blue-50 rounded-md">
                      <p className="text-sm font-medium">Latest Qubic Transaction</p>
                      <p className="text-xs font-mono">{auditLog.qubic_txid}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

