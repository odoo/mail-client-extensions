export const RAINBOW = `<!DOCTYPE html>
<html>
  <div class="o_reward">
    <svg class="o_reward_rainbow_man o_rainbow_root" viewBox="0 0 400 400">
      <defs>
        <radialGradient id="o_reward_gradient_bg" cx="200" cy="200" r="200" gradientUnits="userSpaceOnUse">
          <stop offset="0.3" stop-color="#edeff4" />
          <stop offset="1" stop-color="#edeff4" stop-opacity="0" />
        </radialGradient>
        <symbol id="o_reward_star">
          <path d="M33 15.9C26.3558 13.6951 21.1575 8.4597 19 1.8 19 1.2477 18.5523.8 18 .8 17.4477.8 17 1.2477 17 1.8 14.6431 8.6938 9.0262 13.9736 2 15.9 1.3649 15.9.85 16.4149.85 17.05.85 17.6851 1.3649 18.2 2 18.2 8.6215 20.3845 13.8155 25.5785 16 32.2 16 32.7523 16.4477 33.2 17 33.2 17.5523 33.2 18 32.7523 18 32.2 20.3569 25.3062 25.9738 20.0264 33 18.1 33.6351 18.1 34.15 17.5851 34.15 16.95 34.15 16.3149 33.6351 15.8 33 15.8" fill="#FFFFFF" />
        </symbol>
        <symbol id="o_reward_thumb">
          <path d="M10 52C6 51 3 48 3 44 2 42 3 39 5 38 3 36 2 34 2 32 2 29 3 27 5 26 3 24 2 21 2 19 2 15 7 12 10 12L23 12C23 11 23 11 23 11L23 10C23 8 24 6 25 4 27 2 29 2 31 2 33 2 35 2 36 4 38 5 39 7 39 10L39 38C39 41 37 45 35 47 32 50 28 51 25 52L10 52 10 52Z" fill="#FBFBFC" />
          <polygon fill="#ECF1FF" points="25 11 25 51 5 52 5 12" />
          <path d="M31 0C28 0 26 1 24 3 22 5 21 7 21 10L10 10C8 10 6 11 4 12 2 14 1 16 1 19 1 21 1 24 2 26 1 27 1 29 1 32 1 34 1 36 2 38 1 40 0 42 1 45 1 50 5 53 10 54L25 54C29 54 33 52 36 49 39 46 41 42 41 38L41 10C41 4 36 0 31 0M31 4C34 4 37 6 37 10L37 38C37 41 35 44 33 46 31 48 28 49 25 50L10 50C7 49 5 47 5 44 4 41 6 38 9 37L9 37C6 37 5 35 5 32 5 28 6 26 9 26L9 26C6 26 5 22 5 19 5 16 8 14 11 14L23 14C24 14 25 12 25 11L25 10C25 7 28 4 31 4" fill="#A1ACBA" />
        </symbol>
      </defs>
      <rect width="400" height="400" fill="url(#o_reward_gradient_bg)" />
      <g transform="translate(47 45) scale(0.9)" class="o_reward_rainbow">
        <path d="M270,170a100,100,0,0,0-200,0" class="o_reward_rainbow_line" stroke="#FF9E80" stroke-linecap="round" stroke-width="21" fill="none" stroke-dasharray="600 600" stroke-dashoffset="-600" />
        <path d="M290,170a120,120,0,0,0-240,0" class="o_reward_rainbow_line" stroke="#FFE57F" stroke-linecap="round" stroke-width="21" fill="none" stroke-dasharray="600 600" stroke-dashoffset="-600" />
        <path d="M310,170a140,140,0,0,0-280,0" class="o_reward_rainbow_line" stroke="#80D8FF" stroke-linecap="round" stroke-width="21" fill="none" stroke-dasharray="600 600" stroke-dashoffset="-600" />
        <path d="M330,170a160,160,0,0,0-320,0" class="o_reward_rainbow_line" stroke="#C794BA" stroke-linecap="round" stroke-width="21" fill="none" stroke-dasharray="600 600" stroke-dashoffset="-600" />
      </g>
      <g transform="translate(80 125)">
        <use href="#o_reward_star" transform-origin="center" class="o_reward_box o_reward_star_01" />
      </g>
      <g transform="translate(140 75)">
        <use href="#o_reward_star" transform-origin="center" class="o_reward_box o_reward_star_02" />
      </g>
      <g transform="translate(230 90)">
        <use href="#o_reward_star" transform-origin="center" class="o_reward_box o_reward_star_03" />
      </g>
      <g transform="translate(275 120)">
        <use href="#o_reward_star" transform-origin="center" class="o_reward_box o_reward_star_04" />
      </g>
      <g class="o_reward_face_group o_reward_box" transform-origin="center top">
        <g class="o_reward_face_wrap o_reward_box" transform-origin="center">
          <image class="o_reward_face" x="132" y="125" width="136" height="136" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMzYgMTM2Ij48dGl0bGU+ZmFjZTwvdGl0bGU+PHBhdGggZD0iTTY4IDEzNEE2NiA2NiAwIDEgMCAyIDY4YTY2IDY2IDAgMCAwIDY2IDY2eiIgZmlsbD0iI2ZiZmNmZCIgc3Ryb2tlPSIjYTFhY2JhIiBzdHJva2Utd2lkdGg9IjQiLz48cGF0aCBkPSJNMTA5LjQgMTkuMkE2NC43IDY0LjcgMCAwIDEgMTMyIDY4LjUgNjMuOCA2My44IDAgMCAxIDY4LjUgMTMyYTY0LjcgNjQuNyAwIDAgMS00OS4zLTIyLjZBNjQuOCA2NC44IDAgMCAwIDYxLjUgMTI1IDYzLjggNjMuOCAwIDAgMCAxMjUgNjEuNWE2NC44IDY0LjggMCAwIDAtMTUuNi00Mi4zeiIgc3R5bGU9Imlzb2xhdGlvbjppc29sYXRlIiBmaWxsPSIjZWNmMWZmIi8+PHBhdGggZD0iTTQ5LjEgNjIuMWExMCAxMCAwIDAgMC0xNC4xIDBNMTAxLjEgNjIuMWExMCAxMCAwIDAgMC0xNC4xIDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ExYWNiYSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2Utd2lkdGg9IjUiLz48cGF0aCBkPSJNNDIgODhhMzYuOCAzNi44IDAgMCAwIDUyIDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ExYWNiYSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjUiLz48L3N2Zz4K" />
        </g>
        <g transform="translate(258 174)">
          <use href="#o_reward_thumb" class="o_reward_box o_reward_thumbup" transform-origin="center" />
        </g>
      </g>
    </svg>
    <div class="o_reward_rainbow_man o_reward_msg_container">
      <div class="o_reward_face_group o_reward_face_group_2">
        <svg viewBox="0 0 42 60" preserveAspectRatio="xMinYMax meet" width="37" height="65%" style="overflow: visible; position: relative; margin-left: 1.25rem;">
          <g class="o_reward_box">
            <use href="#o_reward_thumb" x="-60%" y="0" transform="rotate(-90) scale(1 -1)" transform-origin="center" />
          </g>
        </svg>
        <div class="o_reward_msg mx-4">
          <div class="o_reward_msg_card">
            <div class="o_reward_msg_content"> You're all set <br /> You can now close this window and connect with Odoo! </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <style>
    .o_reward {
      will-change: transform;
      z-index: 1;
      animation: reward-fading 0.7s ease-in-out forwards;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }

    .o_reward .o_reward_box {
      transform-box: fill-box;
    }

    .o_reward.o_reward_fading {
      animation: reward-fading-reverse 0.56s ease-in-out forwards;
    }

    .o_reward.o_reward_fading .o_reward_face_group {
      animation: reward-jump-reverse 0.56s ease-in-out forwards;
    }

    .o_reward.o_reward_fading .o_reward_rainbow_line {
      animation: reward-rainbow-reverse 0.7s ease-out forwards;
    }

    .o_reward .o_reward_rainbow_man {
      max-width: 400px;
      position: absolute;
    }

    .o_rainbow_root {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      margin: auto;
      overflow: visible;
    }

    .o_reward .o_reward_rainbow_line {
      animation: reward-rainbow 1.12s ease-out 1 forwards;
    }

    .o_reward .o_reward_face_group {
      animation: reward-jump 1.12s ease-in-out 1;
    }

    .o_reward .o_reward_face_wrap {
      animation: reward-rotate 1.12s cubic-bezier(0.51, 0.92, 0.24, 1.15) 1;
    }

    .o_reward .o_reward_face {
      animation: reward-float 1.4s ease-in-out 1.4s infinite alternate;
    }

    .o_reward .o_reward_star_01,
    .o_reward .o_reward_star_03 {
      animation: reward-stars 1.4s ease-in-out infinite alternate-reverse;
    }

    .o_reward .o_reward_star_02,
    .o_reward .o_reward_star_04 {
      animation: reward-stars 1.68s ease-in-out infinite alternate;
    }

    .o_reward .o_reward_thumbup {
      animation: reward-scale 0.7s ease-in-out 0s infinite alternate;
    }

    .o_reward .o_reward_msg_container {
      aspect-ratio: 1;
      animation: reward-float-reverse 1.4s ease-in-out infinite alternate-reverse;
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      margin: auto;
    }

    .o_reward_msg_content {
      font-family: Arial, Helvetica;
      text-align: center;
      color: #6c757d;
      padding: 1rem 0.75rem;
      background-color: #f8f9fa;
      display: inline-block;
      border: 1px solid #f1f1f1;
      border-top: 0;
    }

    .o_reward_face_group_2 {
      height: 100%;
      width: 75%;
      margin-left: auto;
      margin-right: auto;
    }

    @keyframes reward-fading {
      0% {
        opacity: 0;
      }
    }

    @keyframes reward-fading-reverse {
      100% {
        opacity: 0;
      }
    }

    @keyframes reward-jump {
      0% {
        transform: scale(0.5);
      }

      50% {
        transform: scale(1.05);
      }
    }

    @keyframes reward-jump-reverse {
      50% {
        transform: scale(1.05);
      }

      to {
        transform: scale(0.5);
      }
    }

    @keyframes reward-rainbow {
      to {
        stroke-dashoffset: 0;
      }
    }

    @keyframes reward-rainbow-reverse {
      from {
        stroke-dashoffset: 0;
      }
    }

    @keyframes reward-float {
      to {
        transform: translateY(5px);
      }
    }

    @keyframes reward-float-reverse {
      from {
        transform: translateY(5px);
      }
    }

    @keyframes reward-stars {
      from {
        transform: scale(0.3) rotate(0deg);
      }

      50% {
        transform: scale(1) rotate(20deg);
      }

      to {
        transform: scale(0.3) rotate(80deg);
      }
    }

    @keyframes reward-scale {
      from {
        transform: scale(0.8);
      }
    }

    @keyframes reward-rotate {
      from {
        transform: scale(0.5) rotate(-30deg);
      }
    }
  </style>
</html>`;

export const ERROR_PAGE = `
<html>
    <style>
        .alert {
            color: #721c24;
            background-color: #f5c6cb;
            padding: 20px;
            max-width: 1000px;
            margin: auto;
            text-align: center;
            font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol"
        }
        img {
            max-width: 300px;
            margin-left: calc(50% - 150px);
            margin-bottom: 50px;
        }
        hr {
            border- color: #721c24;
        }
    </style>
    <img src="https://raw.githubusercontent.com/odoo/mail-client-extensions/master/outlook/assets/odoo-full.png">
    <div class="alert">__ERROR_MESSAGE__</div>
</html>`;
