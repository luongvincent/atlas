import Image from "next/image";

const TEAM = [
  {
    name: "Vincent Luong",
    role: "Founder",
    image: "/team-1.png",
  },
  {
    name: "Aadit Rao",
    role: "Lead Developer",
    image: "/team-2.jpeg",
  },
];

export default function TeamPage() {
  return (
    <div className="mx-auto max-w-2xl">
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Our Team</h1>
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
          I grew up in a family where money was always tight, and financial planning wasn&apos;t
          really a conversation we had - we were just trying to get by. My parents are 65 now, and
          they don&apos;t have retirement savings to fall back on. That&apos;s not a rare story. It&apos;s
          the story of a lot of families, especially as the gap between people who have access to
          financial knowledge and people who don&apos;t keeps widening.
        </p>
        <p className="mt-4 text-lg leading-relaxed text-slate-700">
          Atlas Capital exists to close that gap, even in a small way. Financial literacy shouldn&apos;t be
          something you&apos;re only born into - it should be something anyone can pick up, in plain
          language, without a finance degree or a family member who already knows this stuff. My hope
          is that young adults, especially ones who grew up like I did, start thinking about
          retirement early, not because it&apos;s urgent today, but because a little understanding,
          started early, adds up to a lot more freedom later.
        </p>
        <p className="mt-4 text-lg font-medium text-slate-900">- Vincent Luong</p>
      </div>
    </div>
  );
}