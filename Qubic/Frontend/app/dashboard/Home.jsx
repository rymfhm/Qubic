"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import apiClient from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const status = await apiClient.healthCheck();
        setHealthStatus(status);
      } catch (error) {
        console.error("Health check failed:", error);
        setHealthStatus({ status: "unhealthy" });
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-1">Welcome to Qubic Autonomous Execution System</h2>
        <p className="text-gray-400 text-sm">
          Monitor and manage your autonomous task execution with blockchain auditing
        </p>
      </div>

      {/* System Status */}
      <div className="mb-6 p-4 bg-gray-900 border border-gray-800 rounded">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-400 text-sm mb-1">System Status</p>
            <p className={`text-lg font-bold ${healthStatus?.status === 'healthy' ? 'text-green-400' : 'text-red-400'}`}>
              {loading ? "Checking..." : healthStatus?.status === 'healthy' ? "✓ Operational" : "✗ Unavailable"}
            </p>
          </div>
          {healthStatus?.service && (
            <p className="text-xs text-gray-500">{healthStatus.service}</p>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <button
          onClick={() => router.push('/tasks')}
          className="bg-blue-600 hover:bg-blue-700 text-white p-6 rounded-lg border border-blue-500 transition-colors"
        >
          <h3 className="font-semibold mb-2">Create Task</h3>
          <p className="text-sm text-blue-200">Start a new autonomous task execution</p>
        </button>

        <button
          onClick={() => router.push('/executions')}
          className="bg-green-600 hover:bg-green-700 text-white p-6 rounded-lg border border-green-500 transition-colors"
        >
          <h3 className="font-semibold mb-2">View Executions</h3>
          <p className="text-sm text-green-200">Monitor running tasks and agents</p>
        </button>

        <button
          onClick={() => router.push('/wallet')}
          className="bg-purple-600 hover:bg-purple-700 text-white p-6 rounded-lg border border-purple-500 transition-colors"
        >
          <h3 className="font-semibold mb-2">Wallet Management</h3>
          <p className="text-sm text-purple-200">Manage wallet addresses and balances</p>
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: "API Gateway", value: healthStatus?.status === 'healthy' ? "Online" : "Offline", change: healthStatus?.status === 'healthy' ? "✓ Healthy" : "✗ Unhealthy" },
          { label: "Services", value: "6", change: "Running" },
          { label: "Blockchain", value: "Qubic", change: "Connected" },
          { label: "Audit Trail", value: "Active", change: "Recording" },
        ].map((metric, idx) => (
          <div
            key={idx}
            className="bg-gray-900 border border-gray-800 rounded p-4"
          >
            <p className="text-gray-400 text-sm mb-1">{metric.label}</p>
            <p className="text-2xl font-bold text-white">{metric.value}</p>
            <p className={`text-xs mt-2 ${metric.change.includes('✓') ? 'text-green-400' : metric.change.includes('✗') ? 'text-red-400' : 'text-gray-400'}`}>
              {metric.change}
            </p>
          </div>
        ))}
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Start</h3>
        <ol className="list-decimal list-inside space-y-2 text-gray-300 text-sm">
          <li>Navigate to <span className="text-blue-400">Tasks</span> to create a new task</li>
          <li>Monitor task execution in real-time</li>
          <li>Approve tasks that require authorization</li>
          <li>View audit logs with Qubic transaction IDs</li>
        </ol>
      </div>
    </div>
  );
}