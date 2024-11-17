import UploadButton from "./UploadButton";
import { Chat } from "./chat";

export const runtime = 'edge';

const page = () => {
    return (
        <main>
            <div>
                <h1>Dashboard</h1>
                <UploadButton isSubscribed={false} />
                <Chat />
            </div>
        </main>
    )
}




export default page;