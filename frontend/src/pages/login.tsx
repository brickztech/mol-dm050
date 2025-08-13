import { SignInPage, type AuthProvider } from '@toolpad/core/SignInPage';
import { useNavigate } from 'react-router-dom';
import type { User } from 'src/main';
import { useAppStore } from 'src/main';
import { login } from '../api/api';

export default function LoginPage() {
    const navigate = useNavigate();
    const [user, setUser] = useAppStore((state) => [state.user, state.setUser]);
    if (user) {
        // If user is already logged in, redirect to home page
        console.log("user: ", user);
        navigate('/', { replace: true });
    }
    const handleSignIn = async (
        provider: AuthProvider,
        formData?: FormData,
        callbackUrl?: string
    ): Promise<{ ok: boolean; error: string }> => {
        const email = formData?.get('email')?.toString() ?? '';
        const password = formData?.get('password')?.toString() ?? '';
        
        try {
            const result = await login({ email, password });
            console.log('Login successful:', result);
            const user: User = {
                code: result.code,
                name: result.name,
                image: undefined, // Assuming no image is provided
            };
            setUser(user);
            navigate(callbackUrl || '/', { replace: true });
            return { ok: true, error: '' };
        } catch (err: any) {
            return { ok: false, error: err.message ?? 'Login failed' };
        }
    };

    return (
        <SignInPage
            providers={[{ id: 'credentials', name: 'Email and Password' }]}
            signIn={handleSignIn}
        />
    );
}
