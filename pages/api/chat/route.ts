import OpenAI from 'openai';
import { OpenAIStream } from "ai";

export const runtime = 'edge';

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY!,
});

export async function POST(req: Request) {
    // Extract the message from the request
    const { messages } = await req.json();

    // Request the chatbot to generate a response from prompt
    const response = await openai.chat.completions.create({
        model : "gpt-4.0-turbo",
        stream : true,
        messages : messages,
    });

    const stream = OpenAIStream(response);

    return new Response(stream, {
        status: 200,
        headers: {
            'Content-Type': 'text/plain; charset=utf-8',
        },
    });
}