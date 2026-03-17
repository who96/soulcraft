import { NextResponse } from "next/server";
import { seedAgents } from "@/lib/seed";

export async function POST() {
  if (process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Seed is disabled in production" }, { status: 403 });
  }

  const result = seedAgents();
  return NextResponse.json(result);
}
