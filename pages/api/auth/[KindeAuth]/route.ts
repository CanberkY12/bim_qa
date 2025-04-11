import {handleAuth} from "@kinde-oss/kinde-auth-nextjs/server";
import { NextRequest } from "next/server";

// Started but not implemented authorization end.
export async function GET(request: NextRequest, {params}: any) {
    const endpoint = params.kindeAuth;
    return handleAuth(request, endpoint);
}