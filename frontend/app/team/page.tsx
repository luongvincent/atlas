import Image from "next/image";

const TEAM = [
  {
    name: "Vincent Luong",
    role: "Founder / Lead Developer",
    image: "/team-1.png",
  },
  {
    name: "Aadit Rao",
    role: "Developer",
    image: "/team-2.jpeg",
  },
];

export default function TeamPage() {
  return (
    <div className="mx-auto max-w-2xl">
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Team</h1>
        <p className="mt-1 text-base text-slate-600">The two of us building Atlas Capital.</p>
      </div>

      <div className="mt-10 flex justify-center gap-12 sm:gap-16">
        {TEAM.map((member) => (
          <div key={member.name} className="flex flex-col items-center text-center">
            <div className="relative h-28 w-28 overflow-hidden rounded-full border border-slate-200 shadow-card">
              <Image src={member.image} alt={member.name} fill className="object-cover" />
            </div>
            <p className="mt-4 text-lg font-semibold text-slate-900">{member.name}</p>
            <p className="mt-0.5 text-base text-slate-600">{member.role}</p>
          </div>
        ))}
      </div>

      <div className="mx-auto mt-14 max-w-lg text-center">
        <p className="text-base font-semibold uppercase tracking-wide text-brand-700">A note from the founder</p>
        <p className="mt-3 text-lg leading-relaxed text-slate-700">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut
          labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
          laboris nisi ut aliquip ex ea commodo consequat.
        </p>
        <p className="mt-4 text-lg font-medium text-slate-900">- Vincent Luong</p>
      </div>
    </div>
  );
}