export default function Ornament({ className = "" }) {
  return (
    <svg
      className={className}
      viewBox="0 0 360 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="presentation"
      aria-hidden="true"
    >
      <path
        d="M180 20 C 150 4, 120 4, 96 20 C 76 33, 54 33, 34 20"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
      />
      <path
        d="M180 20 C 210 4, 240 4, 264 20 C 284 33, 306 33, 326 20"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
      />
      <ellipse cx="96" cy="20" rx="6" ry="3.2" fill="currentColor" transform="rotate(-28 96 20)" />
      <ellipse cx="264" cy="20" rx="6" ry="3.2" fill="currentColor" transform="rotate(28 264 20)" />
      <ellipse cx="54" cy="33" rx="5" ry="2.6" fill="currentColor" transform="rotate(-10 54 33)" />
      <ellipse cx="306" cy="33" rx="5" ry="2.6" fill="currentColor" transform="rotate(10 306 33)" />
      <path
        d="M180 8 L188 20 L180 32 L172 20 Z"
        fill="currentColor"
      />
      <circle cx="34" cy="20" r="2.4" fill="currentColor" />
      <circle cx="326" cy="20" r="2.4" fill="currentColor" />
    </svg>
  );
}
