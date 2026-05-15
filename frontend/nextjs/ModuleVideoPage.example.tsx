import CourseVideoPlayerClient from "./CourseVideoPlayerClient";
import { getCountryCode } from "./getCountryCode";

type ModuleVideoPageProps = {
  params: { moduleSlug: string };
};

export default async function ModuleVideoPage({ params }: ModuleVideoPageProps) {
  const countryCode = getCountryCode("US");

  return (
    <main>
      <h2>Module: {params.moduleSlug}</h2>
      <p>Country: {countryCode}</p>
      <CourseVideoPlayerClient moduleSlug={params.moduleSlug} countryCode={countryCode} />
    </main>
  );
}

