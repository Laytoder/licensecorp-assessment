export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  wsUrl: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8001',
} as const;

// Validate environment variables
const requiredEnvVars = ['NEXT_PUBLIC_API_URL', 'NEXT_PUBLIC_WS_URL'] as const;

requiredEnvVars.forEach((envVar) => {
  if (!process.env[envVar]) {
    console.warn(`Warning: ${envVar} environment variable is not set`);
  }
}); 