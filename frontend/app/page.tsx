import Intake from '../components/Intake';
import Dashboard from '../components/Dashboard';
import Loading from '../components/Loading';
import Home from '../components/Home';

export default function HomePage() {
  return (
    <main>
      <Home />
      <Intake />
      <Dashboard />
      <Loading />
    </main>
  );
}